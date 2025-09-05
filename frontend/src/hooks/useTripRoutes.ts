import { useRef, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import type { Trip } from '../types/map'
import { createTripPopupContent } from '../utils/mapPopups'
import { getStatusColor } from '../utils/mapStyles'
export const useTripRoutes = (
  map: React.MutableRefObject<mapboxgl.Map | null>,
  onTripClick?: (trip: Trip) => void
) => {
  const tripSources = useRef<string[]>([])
  const selectedTripId = useRef<number | null>(null)
  const activePopups = useRef<mapboxgl.Popup[]>([])

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

  const createPopup = useCallback(
    (content: string) => {
      const popup = new mapboxgl.Popup({
        offset: 25,
        closeButton: true,
        closeOnClick: false,
        className: 'custom-popup',
      }).setHTML(content)

      popup.on('open', () => {
        // Remove this popup from activePopups if it exists, then close others
        activePopups.current = activePopups.current.filter((p) => p !== popup)
        closeAllPopups()
        activePopups.current.push(popup)
      })

      popup.on('close', () => {
        activePopups.current = activePopups.current.filter((p) => p !== popup)
      })

      return popup
    },
    [closeAllPopups]
  )

  const loadChevronImages = useCallback(() => {
    if (!map.current) return

    // Load chevron pattern images if they don't exist
    if (!map.current.hasImage('trip-chevron')) {
      map.current.loadImage('/src/assets/trip-chevron.png', (error, image) => {
        if (error) throw error
        if (image && !map.current!.hasImage('trip-chevron')) {
          map.current!.addImage('trip-chevron', image, { sdf: false })
        }
      })
    }

    if (!map.current.hasImage('trip-chevron-selected')) {
      map.current.loadImage(
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
  }, [map])

  const addTripsToMap = useCallback(
    (trips: Trip[], showTrips: boolean) => {
      if (!map.current) return

      loadChevronImages()

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
            const popup = createPopup(popupContent)

            // Close all other popups when this one opens
            closeAllPopups()

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
    [map, closeAllPopups, onTripClick, createPopup, loadChevronImages]
  )

  const toggleVisibility = useCallback(
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

  const refreshSelectedTrip = useCallback(
    (updatedTrip: Trip, showTrips: boolean) => {
      if (!map.current || !selectedTripId.current) return

      const tripId = selectedTripId.current
      const sourceId = `trip-${tripId}`

      // Remove the existing trip layer and source
      if (map.current?.getSource(sourceId)) {
        if (map.current?.getLayer(`${sourceId}-layer`)) {
          map.current.removeLayer(`${sourceId}-layer`)
        }
        map.current.removeSource(sourceId)

        // Remove from our tracking array
        tripSources.current = tripSources.current.filter(
          (id) => id !== sourceId
        )
      }

      // Re-add the updated trip
      addTripsToMap([updatedTrip], showTrips)

      // Fit map to the updated trip
      setTimeout(() => {
        fitMapToTrip(updatedTrip, true)
      }, 100)
    },
    [map, addTripsToMap, fitMapToTrip]
  )

  return {
    addTripsToMap,
    toggleVisibility,
    fitMapToTrip,
    resetSelectedTrip,
    forceRefreshTrips,
    refreshSelectedTrip,
    closeAllPopups,
  }
}
