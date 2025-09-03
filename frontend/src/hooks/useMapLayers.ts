import { useRef, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import { Stop, Trip, VehiclePosition } from '../types/map'
import {
  createStopPopupContent,
  createTripPopupContent,
  createVehiclePopupContent,
} from '../utils/mapPopups'
import {
  getStatusColor,
  createStopMarkerElement,
  createVehicleArrowElement,
} from '../utils/mapStyles'

export const useMapLayers = (
  map: React.MutableRefObject<mapboxgl.Map | null>,
  onTripClick?: (trip: Trip) => void
) => {
  const stopMarkers = useRef<mapboxgl.Marker[]>([])
  const vehicleMarkers = useRef<mapboxgl.Marker[]>([])
  const tripSources = useRef<string[]>([])
  const activePopups = useRef<mapboxgl.Popup[]>([])
  const selectedTripId = useRef<number | null>(null)

  const closeAllPopups = useCallback(() => {
    activePopups.current.forEach((popup) => popup.remove())
    activePopups.current = []

    // Reset selected trip and update all trip patterns
    if (selectedTripId.current) {
      const prevSelectedId = selectedTripId.current
      selectedTripId.current = null

      // Update the previously selected trip pattern back to normal
      const layerId = `trip-${prevSelectedId}-layer`
      if (map.current?.getLayer(layerId)) {
        map.current.setPaintProperty(layerId, 'line-pattern', 'trip-chevron')
      }
    }
  }, [map])

  // Add click-outside behavior to close all popups
  const setupMapClickHandler = useCallback(() => {
    if (!map.current) return

    map.current.on('click', (e) => {
      // Check if click was on a marker or trip line
      const features = map.current!.queryRenderedFeatures(e.point)
      const clickedOnFeature = features.some(
        (feature) =>
          feature.source && feature.source.toString().startsWith('trip-')
      )

      // If not clicking on a feature and there are active popups, close them
      if (!clickedOnFeature && activePopups.current.length > 0) {
        closeAllPopups()
      }
    })
  }, [map, closeAllPopups])

  const addMarkersToMap = useCallback(
    (stops: Stop[], showStops: boolean) => {
      if (!map.current) return

      // Clear existing markers from ref array only if we don't have the right number
      if (stopMarkers.current.length !== stops.length) {
        stopMarkers.current.forEach((marker) => marker.remove())
        stopMarkers.current = []
      } else {
        // Just update visibility if markers already exist
        stopMarkers.current.forEach((marker) => {
          const markerEl = marker.getElement()
          markerEl.style.display = showStops ? 'block' : 'none'
        })
        return
      }

      stops.forEach((stop) => {
        const lat = parseFloat(stop.latitude!)
        const lng = parseFloat(stop.longitude!)

        // Create marker element
        const markerElement = createStopMarkerElement(stop.stop_type)

        // Create popup content
        const popupContent = createStopPopupContent(stop)

        const popup = new mapboxgl.Popup({
          offset: 25,
          closeButton: true,
          closeOnClick: false,
          className: 'custom-popup',
        }).setHTML(popupContent)

        // Close all other popups when this one opens
        popup.on('open', () => {
          // Remove this popup from activePopups if it exists, then close others
          activePopups.current = activePopups.current.filter((p) => p !== popup)
          closeAllPopups()
          activePopups.current.push(popup)
        })

        // Remove from active popups when closed
        popup.on('close', () => {
          activePopups.current = activePopups.current.filter((p) => p !== popup)
        })

        const marker = new mapboxgl.Marker(markerElement)
          .setLngLat([lng, lat])
          .setPopup(popup)
          .addTo(map.current!)

        // Store marker reference and set initial visibility
        stopMarkers.current.push(marker)

        // Set visibility based on current showStops state
        const markerEl = marker.getElement()
        markerEl.style.display = showStops ? 'block' : 'none'
      })
    },
    [map, closeAllPopups]
  )

  const addTripsToMap = useCallback(
    (trips: Trip[], showTrips: boolean) => {
      if (!map.current) return

      // Always clear existing trip sources to ensure fresh data
      tripSources.current.forEach((sourceId) => {
        if (map.current?.getSource(sourceId)) {
          if (map.current?.getLayer(`${sourceId}-layer`)) {
            map.current.removeLayer(`${sourceId}-layer`)
          }
          map.current.removeSource(sourceId)
        }
      })
      tripSources.current = []

      trips.forEach((trip) => {
        if (!trip.trip_stops || trip.trip_stops.length < 2) return

        // Sort stops by order
        const sortedStops = [...trip.trip_stops].sort(
          (a, b) => a.order - b.order
        )

        // Filter stops with valid coordinates
        const validStops = sortedStops.filter(
          (tripStop) => tripStop.stop.latitude && tripStop.stop.longitude
        )

        if (validStops.length < 2) return

        // Create line coordinates
        const coordinates = validStops.map((tripStop) => [
          parseFloat(tripStop.stop.longitude!),
          parseFloat(tripStop.stop.latitude!),
        ])

        // Create a unique source ID for this trip
        const sourceId = `trip-${trip.id}`
        tripSources.current.push(sourceId)

        // Add source and layer for the trip route
        map.current!.addSource(sourceId, {
          type: 'geojson',
          data: {
            type: 'Feature',
            properties: {
              tripId: trip.id,
              tripName: trip.name,
              vehicleLicense: trip.vehicle_license_plate,
            },
            geometry: {
              type: 'LineString',
              coordinates: coordinates,
            },
          },
        })

        const statusColor = getStatusColor(trip.status)
        // Use selected pattern if this trip is currently selected
        const patternId =
          selectedTripId.current === trip.id
            ? 'trip-chevron-selected'
            : 'trip-chevron'

        // Load chevron pattern images if they don't exist
        if (!map.current!.hasImage('trip-chevron')) {
          map.current!.loadImage(
            '/src/assets/trip-chevron.png',
            (error, image) => {
              if (error) throw error
              if (image && !map.current!.hasImage('trip-chevron')) {
                map.current!.addImage('trip-chevron', image, { sdf: false })
              }
            }
          )
        }

        if (!map.current!.hasImage('trip-chevron-selected')) {
          map.current!.loadImage(
            '/src/assets/trip-chevron-selected.png',
            (error, image) => {
              if (error) throw error
              if (image && !map.current!.hasImage('trip-chevron-selected')) {
                map.current!.addImage('trip-chevron-selected', image, {
                  sdf: false,
                })
              }
            }
          )
        }

        map.current!.addLayer({
          id: `${sourceId}-layer`,
          type: 'line',
          source: sourceId,
          layout: {
            'line-join': 'none',
            'line-cap': 'round',
            visibility: showTrips ? 'visible' : 'none',
          },
          paint: {
            'line-color': statusColor,
            'line-pattern': patternId,
            'line-width': 16,
            'line-opacity': 1.0,
          },
        })

        // Add click handler for trip lines
        map.current!.on('click', `${sourceId}-layer`, (e) => {
          if (onTripClick) {
            // Close all popups and update selected trip pattern
            closeAllPopups()
            selectedTripId.current = trip.id
            const layerId = `${sourceId}-layer`
            if (map.current?.getLayer(layerId)) {
              map.current.setPaintProperty(
                layerId,
                'line-pattern',
                'trip-chevron-selected'
              )
            }

            // Call the trip click callback (for drawer)
            onTripClick(trip)
          } else {
            // Fallback to popup behavior
            const coordinates = e.lngLat

            // Create popup content using the same styling as stops
            const popupContent = createTripPopupContent(trip, validStops)

            const popup = new mapboxgl.Popup({
              offset: 25,
              closeButton: true,
              closeOnClick: false,
              className: 'custom-popup',
            }).setHTML(popupContent)

            // Close all other popups when this one opens
            closeAllPopups()
            activePopups.current.push(popup)

            // Update selected trip pattern
            selectedTripId.current = trip.id
            const layerId = `${sourceId}-layer`
            if (map.current?.getLayer(layerId)) {
              map.current.setPaintProperty(
                layerId,
                'line-pattern',
                'trip-chevron-selected'
              )
            }

            // Remove from active popups when closed and reset pattern
            popup.on('close', () => {
              activePopups.current = activePopups.current.filter(
                (p) => p !== popup
              )

              // Reset pattern back to normal when popup closes
              if (selectedTripId.current === trip.id) {
                selectedTripId.current = null
                if (map.current?.getLayer(layerId)) {
                  map.current.setPaintProperty(
                    layerId,
                    'line-pattern',
                    'trip-chevron'
                  )
                }
              }
            })

            popup.setLngLat(coordinates).addTo(map.current!)
          }
        })

        // Change cursor on hover
        map.current!.on('mouseenter', `${sourceId}-layer`, () => {
          map.current!.getCanvas().style.cursor = 'pointer'
        })

        map.current!.on('mouseleave', `${sourceId}-layer`, () => {
          map.current!.getCanvas().style.cursor = ''
        })
      })
    },
    [map, closeAllPopups, onTripClick]
  )

  const toggleStopVisibility = useCallback((showStops: boolean) => {
    stopMarkers.current.forEach((marker) => {
      const markerEl = marker.getElement()
      markerEl.style.display = showStops ? 'block' : 'none'
    })
  }, [])

  const toggleTripVisibility = useCallback(
    (showTrips: boolean) => {
      if (map.current) {
        tripSources.current.forEach((sourceId) => {
          const layerId = `${sourceId}-layer`
          if (map.current?.getLayer(layerId)) {
            map.current.setLayoutProperty(
              layerId,
              'visibility',
              showTrips ? 'visible' : 'none'
            )
          }
        })

        // Toggle arrow markers visibility
        const arrowElements = document.querySelectorAll('.trip-arrow')
        arrowElements.forEach((element) => {
          ;(element as HTMLElement).style.opacity = showTrips ? '0.8' : '0'
        })
      }
    },
    [map]
  )

  const addVehiclesToMap = useCallback(
    (positions: VehiclePosition[], showVehicles: boolean) => {
      if (!map.current) return

      // Clear existing markers from ref array only if we don't have the right number
      if (vehicleMarkers.current.length !== positions.length) {
        vehicleMarkers.current.forEach((marker) => marker.remove())
        vehicleMarkers.current = []
      } else {
        // Just update visibility if markers already exist
        vehicleMarkers.current.forEach((marker) => {
          const markerEl = marker.getElement()
          markerEl.style.display = showVehicles ? 'block' : 'none'
        })
        return
      }

      positions.forEach((position) => {
        const lat = parseFloat(position.latitude)
        const lng = parseFloat(position.longitude)
        const heading = parseFloat(position.heading)

        // Check if position is live (less than 5 minutes old)
        const positionTime = new Date(position.timestamp)
        const now = new Date()
        const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000)
        const isLive = positionTime > fiveMinutesAgo

        // Create vehicle arrow element with rotation
        const markerElement = createVehicleArrowElement(isLive, heading)

        // Create popup content
        const popupContent = createVehiclePopupContent(position)

        const popup = new mapboxgl.Popup({
          offset: 25,
          closeButton: true,
          closeOnClick: false,
          className: 'custom-popup',
        }).setHTML(popupContent)

        // Close all other popups when this one opens
        popup.on('open', () => {
          // Remove this popup from activePopups if it exists, then close others
          activePopups.current = activePopups.current.filter((p) => p !== popup)
          closeAllPopups()
          activePopups.current.push(popup)
        })

        // Remove from active popups when closed
        popup.on('close', () => {
          activePopups.current = activePopups.current.filter((p) => p !== popup)
        })

        const marker = new mapboxgl.Marker(markerElement)
          .setLngLat([lng, lat])
          .setPopup(popup)
          .addTo(map.current!)

        // Store marker reference and set initial visibility
        vehicleMarkers.current.push(marker)

        // Set visibility based on current showVehicles state
        markerElement.style.display = showVehicles ? 'block' : 'none'
      })
    },
    [map, closeAllPopups]
  )

  const toggleVehicleVisibility = useCallback((showVehicles: boolean) => {
    vehicleMarkers.current.forEach((marker) => {
      const markerEl = marker.getElement()
      markerEl.style.display = showVehicles ? 'block' : 'none'
    })
  }, [])

  const fitMapToStops = useCallback(
    (stops: Stop[]) => {
      if (!map.current || stops.length === 0) return

      const bounds = new mapboxgl.LngLatBounds()

      stops.forEach((stop) => {
        const lat = parseFloat(stop.latitude!)
        const lng = parseFloat(stop.longitude!)
        bounds.extend([lng, lat])
      })

      map.current.fitBounds(bounds, {
        padding: 50,
        maxZoom: 10,
      })
    },
    [map]
  )

  const fitMapToTrip = useCallback(
    (trip: Trip, withDrawerSpace = false) => {
      if (!map.current || !trip.trip_stops || trip.trip_stops.length === 0)
        return

      const bounds = new mapboxgl.LngLatBounds()

      // Add all trip stops to bounds
      trip.trip_stops.forEach((tripStop) => {
        if (tripStop.stop.latitude && tripStop.stop.longitude) {
          const lat = parseFloat(tripStop.stop.latitude)
          const lng = parseFloat(tripStop.stop.longitude)
          bounds.extend([lng, lat])
        }
      })

      // Adjust padding to account for drawer space
      const padding = withDrawerSpace
        ? { top: 100, bottom: 100, left: 100, right: 1000 } // Extra space on right for drawer
        : 50

      map.current.fitBounds(bounds, {
        padding,
        maxZoom: 12,
      })
    },
    [map]
  )

  const resetSelectedTrip = useCallback(() => {
    if (selectedTripId.current) {
      const tripId = selectedTripId.current
      selectedTripId.current = null

      const layerId = `trip-${tripId}-layer`
      if (map.current?.getLayer(layerId)) {
        map.current.setPaintProperty(layerId, 'line-pattern', 'trip-chevron')
      }
    }
  }, [map])

  const forceRefreshTrips = useCallback(
    (trips: Trip[], showTrips: boolean) => {
      if (!map.current) return

      // Clear existing trip sources
      tripSources.current.forEach((sourceId) => {
        if (map.current?.getSource(sourceId)) {
          if (map.current?.getLayer(`${sourceId}-layer`)) {
            map.current.removeLayer(`${sourceId}-layer`)
          }
          map.current.removeSource(sourceId)
        }
      })
      tripSources.current = []

      // Re-add all trips
      addTripsToMap(trips, showTrips)
    },
    [map, addTripsToMap]
  )

  return {
    addMarkersToMap,
    addTripsToMap,
    addVehiclesToMap,
    toggleStopVisibility,
    toggleTripVisibility,
    toggleVehicleVisibility,
    setupMapClickHandler,
    fitMapToStops,
    fitMapToTrip,
    resetSelectedTrip,
    forceRefreshTrips,
  }
}
