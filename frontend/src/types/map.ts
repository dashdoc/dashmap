// Re-export domain types for backward compatibility
export type { Stop, TripStop, Trip } from './domain'

export interface VehiclePosition {
  id: number
  vehicle_id: number
  vehicle_license_plate: string
  vehicle_make_model: string
  latitude: string
  longitude: string
  speed: string
  heading: string
  altitude: string | null
  timestamp: string
  odometer: string | null
  fuel_level: string | null
  engine_status: 'on' | 'off' | 'idle'
  created_at: string
}

export interface MapControls {
  showOrders: boolean
  showVehicles: boolean
  showTrips: boolean
}
