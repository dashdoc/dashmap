export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  company_id: number
  company_name: string
}

export interface Company {
  id: number
  name: string
  email: string
  phone: string
  address: string
  created_at: string
  updated_at: string
}

export interface Vehicle {
  id: number
  company: number
  company_name: string
  license_plate: string
  make: string
  model: string
  year: number
  capacity: string
  driver_name: string
  driver_email: string
  driver_phone: string
  is_active: boolean
  created_at: string
  updated_at: string
}

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

export interface Order {
  id: number
  order_number: string
  customer_name: string
  customer_company: string
  customer_email: string
  customer_phone: string
  pickup_stop: Stop
  delivery_stop: Stop
  goods_description: string
  goods_weight: string | null
  goods_volume: string | null
  goods_type: 'standard' | 'fragile' | 'hazmat' | 'refrigerated' | 'oversized'
  special_instructions: string
  status: 'pending' | 'assigned' | 'in_transit' | 'delivered' | 'cancelled'
  requested_pickup_date: string | null
  requested_delivery_date: string | null
  created_at: string
  updated_at: string
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

// Re-export map types for convenience
export * from './map'
