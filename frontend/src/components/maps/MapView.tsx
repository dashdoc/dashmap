import React, { useEffect, useState, useRef } from 'react'
import mapboxgl from 'mapbox-gl'
import { Box, Text } from '@chakra-ui/react'
import { useAuth } from '../../contexts/AuthContext'
import 'mapbox-gl/dist/mapbox-gl.css'

interface Stop {
  id: number
  name: string
  address: string
  latitude: string | null
  longitude: string | null
  stop_type: 'loading' | 'unloading'
  contact_name: string
  contact_phone: string
  notes: string
}

const MapView: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const [stops, setStops] = useState<Stop[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { token } = useAuth()
  const mapboxToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN
  const apiBaseUrl =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

  useEffect(() => {
    if (!mapboxToken || !token) return

    mapboxgl.accessToken = mapboxToken

    // Add custom CSS for popup close button
    const style = document.createElement('style')
    style.textContent = `
      .custom-popup .mapboxgl-popup-close-button {
        font-size: 20px !important;
        width: 30px !important;
        height: 30px !important;
        line-height: 30px !important;
        text-align: center !important;
        padding: 0 !important;
      }
      .custom-popup .mapboxgl-popup-close-button:focus {
        outline: none !important;
        box-shadow: none !important;
      }
    `
    document.head.appendChild(style)

    fetchStops()

    return () => {
      document.head.removeChild(style)
    }
  }, [mapboxToken, token])

  useEffect(() => {
    if (
      !mapboxToken ||
      !mapContainer.current ||
      map.current ||
      stops.length === 0
    )
      return

    // Initialize map
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [10.0, 54.0], // Center of Europe
      zoom: 4,
    })

    map.current.on('load', () => {
      addMarkersToMap()
      if (stops.length > 0) {
        fitMapToStops()
      }
    })

    // Cleanup
    return () => {
      if (map.current) {
        map.current.remove()
        map.current = null
      }
    }
  }, [stops, mapboxToken])

  const fetchStops = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${apiBaseUrl}/stops/`, {
        headers: {
          Authorization: `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      const stopsWithCoords = data.results.filter(
        (stop: Stop) => stop.latitude && stop.longitude
      )
      setStops(stopsWithCoords)
    } catch (error) {
      console.error('Error fetching stops:', error)
      setError('Failed to load stops')
    } finally {
      setLoading(false)
    }
  }

  const addMarkersToMap = () => {
    if (!map.current) return

    stops.forEach((stop) => {
      const lat = parseFloat(stop.latitude!)
      const lng = parseFloat(stop.longitude!)

      // Create marker element
      const markerElement = document.createElement('div')
      markerElement.style.width = '18px'
      markerElement.style.height = '18px'
      markerElement.style.borderRadius = '50%'
      markerElement.style.backgroundColor =
        stop.stop_type === 'loading' ? '#3182ce' : '#38a169'
      markerElement.style.border = '3px solid white'
      markerElement.style.boxShadow =
        '0 0 0 2px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3)'
      markerElement.style.cursor = 'pointer'

      // Create popup content
      const popupContent = `
        <div style="padding: 8px; min-width: 200px;">
          <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">
            ${stop.name}
          </div>
          <div style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-bottom: 8px; background-color: ${stop.stop_type === 'loading' ? '#ebf8ff' : '#f0fff4'}; color: ${stop.stop_type === 'loading' ? '#3182ce' : '#38a169'};">
            ${stop.stop_type}
          </div>
          <div style="font-size: 12px; color: #666; margin-bottom: 4px;">
            ${stop.address}
          </div>
          ${stop.contact_name ? `<div style="font-size: 12px; margin-bottom: 2px;"><strong>Contact:</strong> ${stop.contact_name}</div>` : ''}
          ${stop.contact_phone ? `<div style="font-size: 12px; margin-bottom: 2px;"><strong>Phone:</strong> ${stop.contact_phone}</div>` : ''}
          ${stop.notes ? `<div style="font-size: 12px;"><strong>Notes:</strong> ${stop.notes}</div>` : ''}
        </div>
      `

      const popup = new mapboxgl.Popup({
        offset: 25,
        closeButton: true,
        closeOnClick: false,
        className: 'custom-popup',
      }).setHTML(popupContent)

      new mapboxgl.Marker(markerElement)
        .setLngLat([lng, lat])
        .setPopup(popup)
        .addTo(map.current!)
    })
  }

  const fitMapToStops = () => {
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
  }

  if (!mapboxToken) {
    return (
      <Box p={4}>
        <Text color="red.500">
          Mapbox token not configured. Please add VITE_MAPBOX_ACCESS_TOKEN to
          your .env file.
        </Text>
      </Box>
    )
  }

  if (loading) {
    return (
      <Box
        height="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text>Loading map...</Text>
      </Box>
    )
  }

  if (error) {
    return (
      <Box
        height="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="red.500">{error}</Text>
      </Box>
    )
  }

  return (
    <Box height="100vh" width="100%" position="relative">
      <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
    </Box>
  )
}

export default MapView
