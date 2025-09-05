import React, { useState, useEffect } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Alert,
  AlertIcon,
  Select,
  Textarea,
  SimpleGrid,
  HStack,
} from '@chakra-ui/react'
import { post, put } from '../../lib/api'
import type { Order, Stop } from '../../types/domain'

interface OrderFormProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  order?: Order | null
}

export const OrderForm: React.FC<OrderFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  order,
}) => {
  const [formData, setFormData] = useState({
    customer_name: '',
    customer_company: '',
    customer_email: '',
    customer_phone: '',
    pickup_stop: '',
    delivery_stop: '',
    goods_description: '',
    goods_weight: '',
    goods_volume: '',
    goods_type: 'standard' as Order['goods_type'],
    special_instructions: '',
    status: 'pending' as Order['status'],
    requested_pickup_date: '',
    requested_delivery_date: '',
  })
  const [stops, setStops] = useState<Stop[]>([])
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStops, setLoadingStops] = useState(false)

  const fetchStops = async () => {
    try {
      setLoadingStops(true)
      // Note: We still need stops for the pickup/delivery selection
      // In a real implementation, you might want to create an internal stops endpoint
      // For now, this will fail gracefully since we removed the public stops API
      setStops([])
    } catch (err) {
      console.error('Error fetching stops:', err)
    } finally {
      setLoadingStops(false)
    }
  }

  useEffect(() => {
    if (isOpen) {
      fetchStops()
    }
  }, [isOpen])

  useEffect(() => {
    if (order) {
      setFormData({
        customer_name: order.customer_name,
        customer_company: order.customer_company,
        customer_email: order.customer_email,
        customer_phone: order.customer_phone,
        pickup_stop: order.pickup_stop.id.toString(),
        delivery_stop: order.delivery_stop.id.toString(),
        goods_description: order.goods_description,
        goods_weight: order.goods_weight || '',
        goods_volume: order.goods_volume || '',
        goods_type: order.goods_type,
        special_instructions: order.special_instructions,
        status: order.status,
        requested_pickup_date: order.requested_pickup_date || '',
        requested_delivery_date: order.requested_delivery_date || '',
      })
    } else {
      setFormData({
        customer_name: '',
        customer_company: '',
        customer_email: '',
        customer_phone: '',
        pickup_stop: '',
        delivery_stop: '',
        goods_description: '',
        goods_weight: '',
        goods_volume: '',
        goods_type: 'standard',
        special_instructions: '',
        status: 'pending',
        requested_pickup_date: '',
        requested_delivery_date: '',
      })
    }
    setError('')
  }, [order, isOpen])

  const handleChange =
    (field: string) =>
    (
      e: React.ChangeEvent<
        HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
      >
    ) => {
      setFormData((prev) => ({
        ...prev,
        [field]: e.target.value,
      }))
    }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (
      !formData.customer_name ||
      !formData.pickup_stop ||
      !formData.delivery_stop ||
      !formData.goods_description
    ) {
      setError('Please fill in all required fields.')
      return
    }

    try {
      setIsLoading(true)
      setError('')

      const payload = {
        customer_name: formData.customer_name,
        customer_company: formData.customer_company,
        customer_email: formData.customer_email,
        customer_phone: formData.customer_phone,
        pickup_stop: parseInt(formData.pickup_stop),
        delivery_stop: parseInt(formData.delivery_stop),
        goods_description: formData.goods_description,
        goods_weight: formData.goods_weight
          ? parseFloat(formData.goods_weight)
          : null,
        goods_volume: formData.goods_volume
          ? parseFloat(formData.goods_volume)
          : null,
        goods_type: formData.goods_type,
        special_instructions: formData.special_instructions,
        status: formData.status,
        requested_pickup_date: formData.requested_pickup_date || null,
        requested_delivery_date: formData.requested_delivery_date || null,
      }

      if (order) {
        await put(`/orders/${order.id}/`, payload)
      } else {
        await post('/orders/', payload)
      }

      onSuccess()
    } catch (err) {
      console.error('Error saving order:', err)
      setError('Failed to save order. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent maxW="900px">
        <form onSubmit={handleSubmit}>
          <ModalHeader>{order ? 'Edit Order' : 'Create New Order'}</ModalHeader>
          <ModalCloseButton />

          <ModalBody>
            <VStack spacing={4} align="stretch">
              {error && (
                <Alert status="error">
                  <AlertIcon />
                  {error}
                </Alert>
              )}

              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Customer Name</FormLabel>
                  <Input
                    value={formData.customer_name}
                    onChange={handleChange('customer_name')}
                    placeholder="Enter customer name"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Customer Company</FormLabel>
                  <Input
                    value={formData.customer_company}
                    onChange={handleChange('customer_company')}
                    placeholder="Enter company name"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Customer Email</FormLabel>
                  <Input
                    type="email"
                    value={formData.customer_email}
                    onChange={handleChange('customer_email')}
                    placeholder="customer@example.com"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Customer Phone</FormLabel>
                  <Input
                    value={formData.customer_phone}
                    onChange={handleChange('customer_phone')}
                    placeholder="+1-555-0123"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Pickup Location</FormLabel>
                  <Select
                    value={formData.pickup_stop}
                    onChange={handleChange('pickup_stop')}
                    placeholder="Select pickup location"
                    isDisabled={loadingStops}
                  >
                    {stops
                      .filter((s) => s.stop_type === 'loading')
                      .map((stop) => (
                        <option key={stop.id} value={stop.id}>
                          {stop.name}
                        </option>
                      ))}
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Delivery Location</FormLabel>
                  <Select
                    value={formData.delivery_stop}
                    onChange={handleChange('delivery_stop')}
                    placeholder="Select delivery location"
                    isDisabled={loadingStops}
                  >
                    {stops
                      .filter((s) => s.stop_type === 'unloading')
                      .map((stop) => (
                        <option key={stop.id} value={stop.id}>
                          {stop.name}
                        </option>
                      ))}
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Goods Description</FormLabel>
                  <Textarea
                    value={formData.goods_description}
                    onChange={handleChange('goods_description')}
                    placeholder="Describe the goods to be transported"
                    rows={3}
                  />
                </FormControl>

                <VStack align="stretch" spacing={4}>
                  <FormControl>
                    <FormLabel>Goods Type</FormLabel>
                    <Select
                      value={formData.goods_type}
                      onChange={handleChange('goods_type')}
                    >
                      <option value="standard">Standard</option>
                      <option value="fragile">Fragile</option>
                      <option value="hazmat">Hazmat</option>
                      <option value="refrigerated">Refrigerated</option>
                      <option value="oversized">Oversized</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Status</FormLabel>
                    <Select
                      value={formData.status}
                      onChange={handleChange('status')}
                    >
                      <option value="pending">Pending</option>
                      <option value="assigned">Assigned</option>
                      <option value="in_transit">In Transit</option>
                      <option value="delivered">Delivered</option>
                      <option value="cancelled">Cancelled</option>
                    </Select>
                  </FormControl>
                </VStack>

                <HStack>
                  <FormControl>
                    <FormLabel>Weight (kg)</FormLabel>
                    <Input
                      type="number"
                      step="0.01"
                      value={formData.goods_weight}
                      onChange={handleChange('goods_weight')}
                      placeholder="0.00"
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Volume (m³)</FormLabel>
                    <Input
                      type="number"
                      step="0.01"
                      value={formData.goods_volume}
                      onChange={handleChange('goods_volume')}
                      placeholder="0.00"
                    />
                  </FormControl>
                </HStack>

                <HStack>
                  <FormControl>
                    <FormLabel>Requested Pickup Date</FormLabel>
                    <Input
                      type="date"
                      value={formData.requested_pickup_date}
                      onChange={handleChange('requested_pickup_date')}
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Requested Delivery Date</FormLabel>
                    <Input
                      type="date"
                      value={formData.requested_delivery_date}
                      onChange={handleChange('requested_delivery_date')}
                    />
                  </FormControl>
                </HStack>

                <FormControl gridColumn="1 / -1">
                  <FormLabel>Special Instructions</FormLabel>
                  <Textarea
                    value={formData.special_instructions}
                    onChange={handleChange('special_instructions')}
                    placeholder="Any special handling instructions..."
                    rows={3}
                  />
                </FormControl>
              </SimpleGrid>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              type="submit"
              colorScheme="blue"
              isLoading={isLoading}
              loadingText={order ? 'Updating...' : 'Creating...'}
            >
              {order ? 'Update Order' : 'Create Order'}
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  )
}
