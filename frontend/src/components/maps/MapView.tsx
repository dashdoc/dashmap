import React, { useEffect, useState, useRef } from 'react'
import mapboxgl from 'mapbox-gl'
import { Box, Text, useDisclosure } from '@chakra-ui/react'
import { useMapData } from '../../hooks/useMapData'
import { useStopMarkers } from '../../hooks/useStopMarkers'
import { useVehicleMarkers } from '../../hooks/useVehicleMarkers'
import { useTripRoutes } from '../../hooks/useTripRoutes'
import { useMapClickHandler } from '../../hooks/useMapClickHandler'
import { useAuth } from '../../contexts/AuthContext'
import type { MapControls, Trip } from '../../types/map'
import { getMapCustomCSS } from '../../utils/mapStyles'
import MapControlsComponent from './MapControls'
import { TripDetailsDrawer } from '../trips/TripDetailsDrawer'
import 'mapbox-gl/dist/mapbox-gl.css'

const MapView: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null)

  // Auth context for API calls
  const { token } = useAuth()

  // Custom hooks for data and layer management
  const { stops, trips, vehiclePositions, loading, error, refetchTrips } =
    useMapData()

  const [shouldRefreshTrips, setShouldRefreshTrips] = useState(false)

  const handleTripUpdated = async () => {
    setShouldRefreshTrips(true)
    await refetchTrips()
  }

  const handleTripStopsChanged = async () => {
    // Refresh the specific selected trip on the map immediately
    if (selectedTrip && token) {
      try {
        // Fetch the latest trip data
        const response = await fetch(
          `http://localhost:8000/api/trips/${selectedTrip.id}/`,
          {
            headers: {
              Authorization: `Token ${token}`,
              'Content-Type': 'application/json',
            },
          }
        )
        if (response.ok) {
          const updatedTrip = await response.json()
          // Update the selected trip state
          setSelectedTrip(updatedTrip)
          // Refresh just this trip's route on the map
          tripRoutes.refreshSelectedTrip(updatedTrip, controls.showTrips)
        }
      } catch (error) {
        console.error('Error fetching updated trip:', error)
      }
    }

    // Also trigger general trip refresh for the list
    setShouldRefreshTrips(true)
    await refetchTrips()
  }

  // Initialize focused hooks
  const stopMarkers = useStopMarkers(map)
  const vehicleMarkers = useVehicleMarkers(map)
  const tripRoutes = useTripRoutes(map, (trip: Trip) => {
    setSelectedTrip(trip)
    onDrawerOpen()
    // Fit map to trip with space for drawer after a short delay
    setTimeout(() => {
      tripRoutes.fitMapToTrip(trip, true)
    }, 100)
  })

  const { setupMapClickHandler } = useMapClickHandler(
    map,
    tripRoutes.closeAllPopups
  )

  // Drawer state
  const {
    isOpen: isDrawerOpen,
    onOpen: onDrawerOpen,
    onClose: onDrawerClose,
  } = useDisclosure()

  // Control states for map layers
  const [controls, setControls] = useState<MapControls>({
    showStops: true,
    showVehicles: true,
    showTrips: true,
  })

  // Track when map is ready for layer operations
  const [mapReady, setMapReady] = useState(false)

  const mapboxToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN

  // Effect to force refresh trips when data changes after an update
  useEffect(() => {
    if (shouldRefreshTrips && mapReady && map.current && trips.length > 0) {
      tripRoutes.forceRefreshTrips(trips, controls.showTrips)
      setShouldRefreshTrips(false)
    }
  }, [trips, shouldRefreshTrips, mapReady, tripRoutes, controls.showTrips])

  // Handle control changes
  const handleControlChange = (control: keyof MapControls, value: boolean) => {
    setControls((prev) => ({ ...prev, [control]: value }))

    if (control === 'showStops') {
      stopMarkers.toggleVisibility(value)
    } else if (control === 'showTrips') {
      tripRoutes.toggleVisibility(value)
    } else if (control === 'showVehicles') {
      vehicleMarkers.toggleVisibility(value)
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

  // Setup map click handler when map is ready
  useEffect(() => {
    if (!mapReady || !map.current) return
    setupMapClickHandler()
  }, [mapReady, setupMapClickHandler])

  // Add layers when both map is ready and data is available
  useEffect(() => {
    if (!mapReady || !map.current || stops.length === 0) return

    stopMarkers.addMarkersToMap(stops, controls.showStops)
    tripRoutes.addTripsToMap(trips, controls.showTrips)
    vehicleMarkers.addVehiclesToMap(vehiclePositions, controls.showVehicles)
  }, [
    mapReady,
    stops,
    trips,
    vehiclePositions,
    stopMarkers,
    tripRoutes,
    vehicleMarkers,
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

      <TripDetailsDrawer
        isOpen={isDrawerOpen}
        onClose={() => {
          setSelectedTrip(null)
          tripRoutes.resetSelectedTrip()
          onDrawerClose()
        }}
        trip={selectedTrip}
        onTripUpdated={handleTripUpdated}
        onTripStopsChanged={handleTripStopsChanged}
      />
    </Box>
  )
}

export default MapView
