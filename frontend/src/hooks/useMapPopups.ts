import { useRef, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'

export const useMapPopups = () => {
  const activePopups = useRef<mapboxgl.Popup[]>([])

  const closeAllPopups = useCallback(() => {
    activePopups.current.forEach((popup) => popup.remove())
    activePopups.current = []
  }, [])

  const addPopup = useCallback((popup: mapboxgl.Popup) => {
    activePopups.current.push(popup)
  }, [])

  const removePopup = useCallback((popup: mapboxgl.Popup) => {
    activePopups.current = activePopups.current.filter((p) => p !== popup)
  }, [])

  const createPopup = useCallback((content: string, options?: mapboxgl.PopupOptions) => {
    const popup = new mapboxgl.Popup({
      offset: 25,
      closeButton: true,
      closeOnClick: false,
      className: 'custom-popup',
      ...options
    }).setHTML(content)

    popup.on('open', () => {
      // Remove this popup from activePopups if it exists, then close others
      removePopup(popup)
      closeAllPopups()
      addPopup(popup)
    })

    popup.on('close', () => {
      removePopup(popup)
    })

    return popup
  }, [closeAllPopups, addPopup, removePopup])

  return {
    closeAllPopups,
    addPopup,
    removePopup,
    createPopup,
    activePopups: activePopups.current
  }
}
