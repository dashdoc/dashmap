import { useState, useEffect, useCallback } from 'react'
import { Stop, Trip } from '../types/map'
import { useAuth } from '../contexts/AuthContext'

export const useMapData = () => {
  const [stops, setStops] = useState<Stop[]>([])
  const [trips, setTrips] = useState<Trip[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { token } = useAuth()
  const apiBaseUrl =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

  const fetchStops = useCallback(async () => {
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
  }, [apiBaseUrl, token])

  const fetchTrips = useCallback(async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/trips/`, {
        headers: {
          Authorization: `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Fetch detailed trip data with stops for each trip
      const tripsWithDetails = await Promise.all(
        data.results.map(async (trip: Trip) => {
          const detailResponse = await fetch(
            `${apiBaseUrl}/trips/${trip.id}/`,
            {
              headers: {
                Authorization: `Token ${token}`,
                'Content-Type': 'application/json',
              },
            }
          )
          if (detailResponse.ok) {
            return await detailResponse.json()
          }
          return trip
        })
      )

      setTrips(tripsWithDetails)
    } catch (error) {
      console.error('Error fetching trips:', error)
    }
  }, [apiBaseUrl, token])

  useEffect(() => {
    if (token) {
      fetchStops()
      fetchTrips()
    }
  }, [fetchStops, fetchTrips])

  return {
    stops,
    trips,
    loading,
    error,
    refetchStops: fetchStops,
    refetchTrips: fetchTrips,
  }
}
