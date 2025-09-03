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
  createArrowElement,
  createVehicleArrowElement,
} from '../utils/mapStyles'

export const useMapLayers = (
  map: React.MutableRefObject<mapboxgl.Map | null>
) => {
  const stopMarkers = useRef<mapboxgl.Marker[]>([])
  const vehicleMarkers = useRef<mapboxgl.Marker[]>([])
  const tripSources = useRef<string[]>([])

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
    [map]
  )

  const addTripsToMap = useCallback(
    (trips: Trip[], showTrips: boolean) => {
      if (!map.current) return

      // Check if we already have the right number of trip sources
      const expectedSources = trips.filter(
        (trip) => trip.trip_stops && trip.trip_stops.length >= 2
      ).length

      if (tripSources.current.length === expectedSources) {
        // Just toggle visibility if sources already exist
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
        return
      }

      // Clear existing trip sources if count doesn't match
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

        map.current!.addLayer({
          id: `${sourceId}-layer`,
          type: 'line',
          source: sourceId,
          layout: {
            'line-join': 'round',
            'line-cap': 'round',
          },
          paint: {
            'line-color': statusColor,
            'line-width': 3,
            'line-opacity': 0.8,
          },
        })

        // Add directional arrows at midpoints
        for (let i = 0; i < coordinates.length - 1; i++) {
          const start = coordinates[i]
          const end = coordinates[i + 1]
          const midPoint = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]

          // Calculate bearing for arrow direction
          const bearing =
            (Math.atan2(end[1] - start[1], end[0] - start[0]) * 180) / Math.PI

          // Create arrow marker
          const arrowElement = createArrowElement(statusColor)
          arrowElement.style.transform = `rotate(${bearing + 90}deg)`
          arrowElement.style.opacity = showTrips ? '0.8' : '0'
          arrowElement.classList.add('trip-arrow') // Add class for easier identification

          new mapboxgl.Marker({
            element: arrowElement,
            anchor: 'center',
          })
            .setLngLat(midPoint as [number, number])
            .addTo(map.current!)
        }

        // Add click handler for trip lines
        map.current!.on('click', `${sourceId}-layer`, (e) => {
          const coordinates = e.lngLat

          // Create popup content using the same styling as stops
          const popupContent = createTripPopupContent(trip, validStops)

          const popup = new mapboxgl.Popup({
            offset: 25,
            closeButton: true,
            closeOnClick: false,
            className: 'custom-popup',
          }).setHTML(popupContent)

          popup.setLngLat(coordinates).addTo(map.current!)
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
    [map]
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
    [map]
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

  return {
    addMarkersToMap,
    addTripsToMap,
    addVehiclesToMap,
    toggleStopVisibility,
    toggleTripVisibility,
    toggleVehicleVisibility,
    fitMapToStops,
  }
}
