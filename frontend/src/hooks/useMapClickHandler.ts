import { useCallback } from 'react'
import mapboxgl from 'mapbox-gl'

export const useMapClickHandler = (
  map: React.MutableRefObject<mapboxgl.Map | null>,
  closeAllPopups: () => void
) => {
  const setupMapClickHandler = useCallback(() => {
    if (!map.current) return

    map.current.on('click', (e) => {
      // Check if click was on a marker or trip line
      const features = map.current!.queryRenderedFeatures(e.point)
      const clickedOnFeature = features.some(
        (feature) =>
          feature.source && feature.source.toString().startsWith('trip-')
      )

      // If not clicking on a feature, close all popups
      if (!clickedOnFeature) {
        closeAllPopups()
      }
    })
  }, [map, closeAllPopups])

  return {
    setupMapClickHandler
  }
}
