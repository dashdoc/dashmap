export interface Stop {
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

export interface TripStop {
  id: number
  stop: Stop
  order: number
  planned_arrival_time: string
  actual_arrival_datetime: string | null
  actual_departure_datetime: string | null
  notes: string
  is_completed: boolean
}

export interface Trip {
  id: number
  vehicle: number
  vehicle_license_plate: string
  dispatcher: number
  dispatcher_name: string
  name: string
  status: 'draft' | 'planned' | 'in_progress' | 'completed' | 'cancelled'
  planned_start_date: string
  planned_start_time: string
  actual_start_datetime: string | null
  actual_end_datetime: string | null
  notes: string
  driver_notified: boolean
  created_at: string
  updated_at: string
  trip_stops?: TripStop[]
}

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
  showStops: boolean
  showVehicles: boolean
  showTrips: boolean
}
