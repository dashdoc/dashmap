import { useRef, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import type { VehiclePosition } from '../types/map'
import { createVehiclePopupContent } from '../utils/mapPopups'
import { createVehicleArrowElement } from '../utils/mapStyles'
export const useVehicleMarkers = (
  map: React.MutableRefObject<mapboxgl.Map | null>
) => {
  const vehicleMarkers = useRef<mapboxgl.Marker[]>([])
  const activePopups = useRef<mapboxgl.Popup[]>([])

  const createPopup = useCallback((content: string) => {
    const popup = new mapboxgl.Popup({
      offset: 25,
      closeButton: true,
      closeOnClick: false,
      className: 'custom-popup',
    }).setHTML(content)

    popup.on('open', () => {
      // Remove this popup from activePopups if it exists, then close others
      activePopups.current = activePopups.current.filter((p) => p !== popup)
      activePopups.current.forEach((p) => p.remove())
      activePopups.current = [popup]
    })

    popup.on('close', () => {
      activePopups.current = activePopups.current.filter((p) => p !== popup)
    })

    return popup
  }, [])

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
        const popup = createPopup(popupContent)

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
    [map, createPopup]
  )

  const toggleVisibility = useCallback((showVehicles: boolean) => {
    vehicleMarkers.current.forEach((marker) => {
      const markerEl = marker.getElement()
      markerEl.style.display = showVehicles ? 'block' : 'none'
    })
  }, [])

  const clearMarkers = useCallback(() => {
    vehicleMarkers.current.forEach((marker) => marker.remove())
    vehicleMarkers.current = []
  }, [])

  return {
    addVehiclesToMap,
    toggleVisibility,
    clearMarkers,
  }
}
