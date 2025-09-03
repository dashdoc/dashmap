import React, { useEffect, useState, useRef } from 'react'
import mapboxgl from 'mapbox-gl'
import { Box, Text } from '@chakra-ui/react'
import { useMapData } from '../../hooks/useMapData'
import { useMapLayers } from '../../hooks/useMapLayers'
import { MapControls } from '../../types/map'
import { getMapCustomCSS } from '../../utils/mapStyles'
import MapControlsComponent from './MapControls'
import 'mapbox-gl/dist/mapbox-gl.css'

const MapView: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)

  // Custom hooks for data and layer management
  const { stops, trips, vehiclePositions, loading, error } = useMapData()
  const {
    addMarkersToMap,
    addTripsToMap,
    addVehiclesToMap,
    toggleStopVisibility,
    toggleTripVisibility,
    toggleVehicleVisibility,
  } = useMapLayers(map)

  // Control states for map layers
  const [controls, setControls] = useState<MapControls>({
    showStops: true,
    showVehicles: true,
    showTrips: true,
  })

  // Track when map is ready for layer operations
  const [mapReady, setMapReady] = useState(false)

  const mapboxToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN

  // Handle control changes
  const handleControlChange = (control: keyof MapControls, value: boolean) => {
    setControls((prev) => ({ ...prev, [control]: value }))

    if (control === 'showStops') {
      toggleStopVisibility(value)
    } else if (control === 'showTrips') {
      toggleTripVisibility(value)
    } else if (control === 'showVehicles') {
      toggleVehicleVisibility(value)
    }
  }

  // Initialize map and add custom CSS
  useEffect(() => {
    if (!mapboxToken) return

    mapboxgl.accessToken = mapboxToken

    // Add custom CSS for popup close button
    const style = document.createElement('style')
    style.textContent = getMapCustomCSS()
    document.head.appendChild(style)

    return () => {
      document.head.removeChild(style)
    }
  }, [mapboxToken])

  // Initialize map once when container and token are available
  useEffect(() => {
    if (!mapboxToken || map.current) return

    // Use setTimeout to ensure DOM is fully ready
    const initMap = () => {
      if (!mapContainer.current) {
        setTimeout(initMap, 100)
        return
      }

      try {
        // Initialize map
        map.current = new mapboxgl.Map({
          container: mapContainer.current,
          style: 'mapbox://styles/mapbox/navigation-night-v1',
          center: [2.3522, 48.8566], // Paris, France
          zoom: 6,
        })

        map.current.on('load', () => {
          setMapReady(true)
        })

        map.current.on('error', (e) => {
          console.error('Map error:', e)
        })
      } catch (error) {
        console.error('Failed to create map:', error)
      }
    }

    // Start initialization
    setTimeout(initMap, 0)

    // Cleanup
    return () => {
      if (map.current) {
        map.current.remove()
        map.current = null
        setMapReady(false)
      }
    }
  }, [mapboxToken])

  // Add layers when both map is ready and data is available
  useEffect(() => {
    if (!mapReady || !map.current || stops.length === 0) return

    addMarkersToMap(stops, controls.showStops)
    addTripsToMap(trips, controls.showTrips)
    addVehiclesToMap(vehiclePositions, controls.showVehicles)
  }, [
    mapReady,
    stops,
    trips,
    vehiclePositions,
    addMarkersToMap,
    addTripsToMap,
    addVehiclesToMap,
    controls.showStops,
    controls.showTrips,
    controls.showVehicles,
  ])

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
      <MapControlsComponent
        controls={controls}
        onControlChange={handleControlChange}
      />
    </Box>
  )
}

export default MapView
