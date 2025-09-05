import { useRef, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import type { Stop } from '../types/map'
import { createStopPopupContent } from '../utils/mapPopups'
import { createStopMarkerElement } from '../utils/mapStyles'
export const useStopMarkers = (
  map: React.MutableRefObject<mapboxgl.Map | null>
) => {
  const stopMarkers = useRef<mapboxgl.Marker[]>([])
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
        const popup = createPopup(popupContent)

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
    [map, createPopup]
  )

  const toggleVisibility = useCallback((showStops: boolean) => {
    stopMarkers.current.forEach((marker) => {
      const markerEl = marker.getElement()
      markerEl.style.display = showStops ? 'block' : 'none'
    })
  }, [])

  const clearMarkers = useCallback(() => {
    stopMarkers.current.forEach((marker) => marker.remove())
    stopMarkers.current = []
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
    toggleVisibility,
    clearMarkers,
    fitMapToStops,
  }
}
