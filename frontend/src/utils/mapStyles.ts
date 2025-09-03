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

export const createVehicleArrowElement = (
  isLive: boolean = true,
  heading: number = 0
): HTMLDivElement => {
  const container = document.createElement('div')
  container.style.width = '24px'
  container.style.height = '24px'
  container.style.cursor = 'pointer'

  const arrowElement = document.createElement('div')
  arrowElement.style.width = '24px'
  arrowElement.style.height = '24px'
  arrowElement.style.backgroundImage = isLive
    ? 'url(/src/assets/position-live.png)'
    : 'url(/src/assets/position-outdated.png)'
  arrowElement.style.backgroundSize = 'contain'
  arrowElement.style.backgroundRepeat = 'no-repeat'
  arrowElement.style.backgroundPosition = 'center'
  arrowElement.style.transform = `rotate(${heading}deg)`
  arrowElement.style.transformOrigin = 'center'

  container.appendChild(arrowElement)

  return container
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
