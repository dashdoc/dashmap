import { useCallback, useRef } from 'react'
import mapboxgl from 'mapbox-gl'
import type { Order } from '../../../types/domain'
import { createStopMarkerElement } from '../utils/mapStyles'

export const useOrderMarkers = (
  mapRef: React.RefObject<mapboxgl.Map | null>
) => {
  const markersRef = useRef<mapboxgl.Marker[]>([])

  const clearMarkers = useCallback(() => {
    markersRef.current.forEach((marker) => marker.remove())
    markersRef.current = []
  }, [])

  const addMarkersToMap = useCallback(
    (orders: Order[], visible: boolean) => {
      if (!mapRef.current || !orders.length) return

      clearMarkers()

      orders.forEach((order) => {
        // Add pickup marker
        if (order.pickup_stop.latitude && order.pickup_stop.longitude) {
          const pickupEl = createStopMarkerElement('loading')
          pickupEl.style.display = visible ? 'block' : 'none'

          const pickupPopup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
            <div>
              <h3>Pickup: ${order.order_number}</h3>
              <p><strong>Customer:</strong> ${order.customer_name}</p>
              <p><strong>Company:</strong> ${order.customer_company}</p>
              <p><strong>Location:</strong> ${order.pickup_stop.name}</p>
              <p><strong>Goods:</strong> ${order.goods_description}</p>
              <p><strong>Status:</strong> ${order.status}</p>
            </div>
          `)

          const pickupMarker = new mapboxgl.Marker(pickupEl)
            .setLngLat([
              parseFloat(order.pickup_stop.longitude),
              parseFloat(order.pickup_stop.latitude),
            ])
            .setPopup(pickupPopup)
            .addTo(mapRef.current!)

          markersRef.current.push(pickupMarker)
        }

        // Add delivery marker
        if (order.delivery_stop.latitude && order.delivery_stop.longitude) {
          const deliveryEl = createStopMarkerElement('unloading')
          deliveryEl.style.display = visible ? 'block' : 'none'

          const deliveryPopup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
            <div>
              <h3>Delivery: ${order.order_number}</h3>
              <p><strong>Customer:</strong> ${order.customer_name}</p>
              <p><strong>Company:</strong> ${order.customer_company}</p>
              <p><strong>Location:</strong> ${order.delivery_stop.name}</p>
              <p><strong>Goods:</strong> ${order.goods_description}</p>
              <p><strong>Status:</strong> ${order.status}</p>
            </div>
          `)

          const deliveryMarker = new mapboxgl.Marker(deliveryEl)
            .setLngLat([
              parseFloat(order.delivery_stop.longitude),
              parseFloat(order.delivery_stop.latitude),
            ])
            .setPopup(deliveryPopup)
            .addTo(mapRef.current!)

          markersRef.current.push(deliveryMarker)
        }
      })
    },
    [mapRef, clearMarkers]
  )

  const toggleVisibility = useCallback((visible: boolean) => {
    markersRef.current.forEach((marker) => {
      const element = marker.getElement()
      if (element) {
        element.style.display = visible ? 'block' : 'none'
      }
    })
  }, [])

  return {
    addMarkersToMap,
    toggleVisibility,
    clearMarkers,
  }
}
