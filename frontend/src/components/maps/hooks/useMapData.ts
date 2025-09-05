import { useState, useEffect, useCallback } from 'react'
import type { Trip, VehiclePosition } from '../../../types/map'
import type { Order } from '../../../types/domain'
import { useAuth } from '../../../contexts/AuthContext'
import { get } from '../../../lib/api'

export const useMapData = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [trips, setTrips] = useState<Trip[]>([])
  const [vehiclePositions, setVehiclePositions] = useState<VehiclePosition[]>(
    []
  )
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { token } = useAuth()

  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true)
      const orders = await get<Order[]>('/orders/')
      setOrders(orders)
      setError('')
    } catch (error) {
      console.error('Error fetching orders:', error)
      setError('Failed to load orders')
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
      fetchOrders()
      fetchTrips()
      fetchVehiclePositions()
    }
  }, [token, fetchOrders, fetchTrips, fetchVehiclePositions])

  return {
    orders,
    trips,
    vehiclePositions,
    loading,
    error,
    refetchOrders: fetchOrders,
    refetchTrips: fetchTrips,
    refetchVehiclePositions: fetchVehiclePositions,
  }
}
