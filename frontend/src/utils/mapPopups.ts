import { Stop, Trip, TripStop, VehiclePosition } from '../types/map'

export const createStopPopupContent = (stop: Stop): string => {
  return `
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
}

export const createTripPopupContent = (
  trip: Trip,
  validStops: TripStop[]
): string => {
  const getStatusBackground = (status: string) => {
    switch (status) {
      case 'completed':
        return '#f0fff4'
      case 'in_progress':
        return '#fefcbf'
      case 'cancelled':
        return '#fed7d7'
      default:
        return '#ebf8ff'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#38a169'
      case 'in_progress':
        return '#d69e2e'
      case 'cancelled':
        return '#e53e3e'
      default:
        return '#3182ce'
    }
  }

  return `
    <div style="padding: 8px; min-width: 200px;">
      <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">
        ${trip.name}
      </div>
      <div style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-bottom: 8px; background-color: ${getStatusBackground(trip.status)}; color: ${getStatusColor(trip.status)};">
        ${trip.status}
      </div>
      <div style="font-size: 12px; color: #666; margin-bottom: 4px;">
        Vehicle: ${trip.vehicle_license_plate}
      </div>
      <div style="font-size: 12px; margin-bottom: 2px;"><strong>Stops:</strong> ${validStops.length}</div>
      ${trip.dispatcher_name ? `<div style="font-size: 12px; margin-bottom: 2px;"><strong>Dispatcher:</strong> ${trip.dispatcher_name}</div>` : ''}
      ${trip.planned_start_date ? `<div style="font-size: 12px;"><strong>Planned Start:</strong> ${trip.planned_start_date} ${trip.planned_start_time}</div>` : ''}
    </div>
  `
}

export const createVehiclePopupContent = (
  position: VehiclePosition
): string => {
  const getEngineStatusBackground = (status: string) => {
    switch (status) {
      case 'on':
        return '#f0fff4'
      case 'idle':
        return '#fefcbf'
      case 'off':
        return '#f7fafc'
      default:
        return '#f7fafc'
    }
  }

  const getEngineStatusColor = (status: string) => {
    switch (status) {
      case 'on':
        return '#38a169'
      case 'idle':
        return '#d69e2e'
      case 'off':
        return '#666'
      default:
        return '#666'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString()
  }

  return `
    <div style="padding: 8px; min-width: 200px;">
      <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">
        ${position.vehicle_license_plate}
      </div>
      <div style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-bottom: 8px; background-color: ${getEngineStatusBackground(position.engine_status)}; color: ${getEngineStatusColor(position.engine_status)};">
        ${position.engine_status}
      </div>
      <div style="font-size: 12px; color: #666; margin-bottom: 4px;">
        ${position.vehicle_make_model}
      </div>
      <div style="font-size: 12px; margin-bottom: 2px;"><strong>Speed:</strong> ${parseFloat(position.speed).toFixed(0)} km/h</div>
      <div style="font-size: 12px; margin-bottom: 2px;"><strong>Heading:</strong> ${parseFloat(position.heading).toFixed(0)}°</div>
      ${position.fuel_level ? `<div style="font-size: 12px; margin-bottom: 2px;"><strong>Fuel:</strong> ${parseFloat(position.fuel_level).toFixed(0)}%</div>` : ''}
      ${position.odometer ? `<div style="font-size: 12px; margin-bottom: 2px;"><strong>Odometer:</strong> ${parseFloat(position.odometer).toFixed(0)} km</div>` : ''}
      <div style="font-size: 11px; color: #999;"><strong>Last Update:</strong> ${formatTimestamp(position.timestamp)}</div>
    </div>
  `
}
