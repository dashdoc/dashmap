export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'draft':
      return '#9CA3AF'
    case 'planned':
      return '#3B82F6'
    case 'in_progress':
      return '#F59E0B'
    case 'completed':
      return '#10B981'
    case 'cancelled':
      return '#EF4444'
    default:
      return '#6B7280'
  }
}

export const createStopMarkerElement = (
  stopType: 'loading' | 'unloading'
): HTMLDivElement => {
  const markerElement = document.createElement('div')
  markerElement.style.width = '18px'
  markerElement.style.height = '18px'
  markerElement.style.borderRadius = '50%'
  markerElement.style.backgroundColor =
    stopType === 'loading' ? '#3182ce' : '#38a169'
  markerElement.style.border = '3px solid white'
  markerElement.style.boxShadow =
    '0 0 0 2px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3)'
  markerElement.style.cursor = 'pointer'
  return markerElement
}

export const createArrowElement = (color: string): HTMLDivElement => {
  const arrowElement = document.createElement('div')
  arrowElement.style.width = '0'
  arrowElement.style.height = '0'
  arrowElement.style.borderLeft = '8px solid transparent'
  arrowElement.style.borderRight = '8px solid transparent'
  arrowElement.style.borderBottom = `12px solid ${color}`
  arrowElement.style.opacity = '0.8'
  return arrowElement
}

export const getMapCustomCSS = (): string => {
  return `
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
}
