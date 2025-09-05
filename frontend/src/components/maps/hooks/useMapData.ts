import { useState, useEffect, useCallback } from 'react'
import type { Stop, Trip, VehiclePosition } from '../../../types/map'
import { useAuth } from '../../../contexts/AuthContext'
import { get } from '../../../lib/api'

export const useMapData = () => {
  const [stops, setStops] = useState<Stop[]>([])
  const [trips, setTrips] = useState<Trip[]>([])
  const [vehiclePositions, setVehiclePositions] = useState<VehiclePosition[]>(
    []
  )
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { token } = useAuth()

  const fetchStops = useCallback(async () => {
    try {
      setLoading(true)
      const stops = await get<Stop[]>('/stops/')
      const stopsWithCoords = stops.filter(
        (stop: Stop) => stop.latitude && stop.longitude
      )
      setStops(stopsWithCoords)
    } catch (error) {
      console.error('Error fetching stops:', error)
      setError('Failed to load stops')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchTrips = useCallback(async () => {
    try {
      const trips = await get<Trip[]>('/trips/')
      setTrips(trips)
    } catch (error) {
      console.error('Error fetching trips:', error)
    }
  }, [])

  const fetchVehiclePositions = useCallback(async () => {
    try {
      const positions = await get<VehiclePosition[]>('/positions/latest/')
      setVehiclePositions(positions)
    } catch (error) {
      console.error('Error fetching vehicle positions:', error)
    }
  }, [])

  useEffect(() => {
    if (token) {
      fetchStops()
      fetchTrips()
      fetchVehiclePositions()
    }
  }, [token, fetchStops, fetchTrips, fetchVehiclePositions])

  return {
    stops,
    trips,
    vehiclePositions,
    loading,
    error,
    refetchStops: fetchStops,
    refetchTrips: fetchTrips,
    refetchVehiclePositions: fetchVehiclePositions,
  }
}
