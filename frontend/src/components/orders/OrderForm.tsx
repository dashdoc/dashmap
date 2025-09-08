import React, { useState, useEffect } from 'react'
import {
  Drawer,
  DrawerBody,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
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
  Box,
  Text,
  useDisclosure,
} from '@chakra-ui/react'
import { post, put } from '../../lib/api'
import type { Order } from '../../types/domain'
import { StopForm } from './StopForm'

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
    pickup_stop: {
      id: undefined as number | undefined,
      name: '',
      address: '',
      contact_name: '',
      contact_phone: '',
      notes: '',
    },
    delivery_stop: {
      id: undefined as number | undefined,
      name: '',
      address: '',
      contact_name: '',
      contact_phone: '',
      notes: '',
    },
    goods_description: '',
    goods_weight: '',
    goods_volume: '',
    goods_type: 'standard' as Order['goods_type'],
    special_instructions: '',
    status: 'pending' as Order['status'],
    requested_pickup_date: '',
    requested_delivery_date: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [editingStopType, setEditingStopType] = useState<
    'pickup' | 'delivery' | null
  >(null)
  const {
    isOpen: isStopFormOpen,
    onOpen: onStopFormOpen,
    onClose: onStopFormClose,
  } = useDisclosure()

  useEffect(() => {
    if (order) {
      setFormData({
        customer_name: order.customer_name,
        customer_company: order.customer_company,
        customer_email: order.customer_email,
        customer_phone: order.customer_phone,
        pickup_stop: {
          id: order.pickup_stop.id,
          name: order.pickup_stop.name,
          address: order.pickup_stop.address,
          contact_name: order.pickup_stop.contact_name,
          contact_phone: order.pickup_stop.contact_phone,
          notes: order.pickup_stop.notes,
        },
        delivery_stop: {
          id: order.delivery_stop.id,
          name: order.delivery_stop.name,
          address: order.delivery_stop.address,
          contact_name: order.delivery_stop.contact_name,
          contact_phone: order.delivery_stop.contact_phone,
          notes: order.delivery_stop.notes,
        },
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
        pickup_stop: {
          id: undefined as number | undefined,
          name: '',
          address: '',
          contact_name: '',
          contact_phone: '',
          notes: '',
        },
        delivery_stop: {
          id: undefined as number | undefined,
          name: '',
          address: '',
          contact_name: '',
          contact_phone: '',
          notes: '',
        },
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
    (field: string, subField?: string) =>
    (
      e: React.ChangeEvent<
        HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
      >
    ) => {
      if (subField) {
        setFormData((prev) => ({
          ...prev,
          [field]: {
            ...(prev[field as keyof typeof prev] as Record<string, unknown>),
            [subField]: e.target.value,
          },
        }))
      } else {
        setFormData((prev) => ({
          ...prev,
          [field]: e.target.value,
        }))
      }
    }

  const openStopForm = (stopType: 'pickup' | 'delivery') => {
    setEditingStopType(stopType)
    onStopFormOpen()
  }

  const handleStopSave = (stopData: {
    id?: number
    name: string
    address: string
    contact_name: string
    contact_phone: string
    notes: string
  }) => {
    if (editingStopType) {
      setFormData((prev) => ({
        ...prev,
        [editingStopType === 'pickup' ? 'pickup_stop' : 'delivery_stop']:
          stopData,
      }))
    }
  }

  const handleStopFormClose = () => {
    onStopFormClose()
    setEditingStopType(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (
      !formData.customer_name ||
      !formData.pickup_stop.name ||
      !formData.pickup_stop.address ||
      !formData.delivery_stop.name ||
      !formData.delivery_stop.address ||
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
        pickup_stop: formData.pickup_stop.id
          ? formData.pickup_stop.id
          : {
              name: formData.pickup_stop.name,
              address: formData.pickup_stop.address,
              stop_type: 'loading' as const,
              contact_name: formData.pickup_stop.contact_name,
              contact_phone: formData.pickup_stop.contact_phone,
              notes: formData.pickup_stop.notes,
              latitude: null,
              longitude: null,
            },
        delivery_stop: formData.delivery_stop.id
          ? formData.delivery_stop.id
          : {
              name: formData.delivery_stop.name,
              address: formData.delivery_stop.address,
              stop_type: 'unloading' as const,
              contact_name: formData.delivery_stop.contact_name,
              contact_phone: formData.delivery_stop.contact_phone,
              notes: formData.delivery_stop.notes,
              latitude: null,
              longitude: null,
            },
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
    <Drawer isOpen={isOpen} placement="right" onClose={onClose} size="xl">
      <DrawerOverlay />
      <DrawerContent maxW="900px">
        <DrawerCloseButton />
        <DrawerHeader>{order ? 'Edit Order' : 'Create New Order'}</DrawerHeader>
        <form onSubmit={handleSubmit}>
          <DrawerBody>
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
                  <Box
                    p={4}
                    border="1px"
                    borderColor={
                      formData.pickup_stop.name ? 'blue.200' : 'gray.200'
                    }
                    borderRadius="md"
                    bg={formData.pickup_stop.name ? 'blue.50' : 'gray.50'}
                  >
                    {formData.pickup_stop.name ? (
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="bold" color="blue.700">
                          {formData.pickup_stop.name}
                        </Text>
                        <Text fontSize="sm" color="gray.600">
                          {formData.pickup_stop.address}
                        </Text>
                        {formData.pickup_stop.contact_name && (
                          <Text fontSize="sm">
                            Contact: {formData.pickup_stop.contact_name}
                          </Text>
                        )}
                        <Button
                          size="sm"
                          colorScheme="blue"
                          variant="outline"
                          onClick={() => openStopForm('pickup')}
                          mt={2}
                        >
                          Edit Pickup Location
                        </Button>
                      </VStack>
                    ) : (
                      <VStack>
                        <Text color="gray.500">
                          No pickup location selected
                        </Text>
                        <Button
                          colorScheme="blue"
                          onClick={() => openStopForm('pickup')}
                        >
                          Add Pickup Location
                        </Button>
                      </VStack>
                    )}
                  </Box>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Delivery Location</FormLabel>
                  <Box
                    p={4}
                    border="1px"
                    borderColor={
                      formData.delivery_stop.name ? 'green.200' : 'gray.200'
                    }
                    borderRadius="md"
                    bg={formData.delivery_stop.name ? 'green.50' : 'gray.50'}
                  >
                    {formData.delivery_stop.name ? (
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="bold" color="green.700">
                          {formData.delivery_stop.name}
                        </Text>
                        <Text fontSize="sm" color="gray.600">
                          {formData.delivery_stop.address}
                        </Text>
                        {formData.delivery_stop.contact_name && (
                          <Text fontSize="sm">
                            Contact: {formData.delivery_stop.contact_name}
                          </Text>
                        )}
                        <Button
                          size="sm"
                          colorScheme="green"
                          variant="outline"
                          onClick={() => openStopForm('delivery')}
                          mt={2}
                        >
                          Edit Delivery Location
                        </Button>
                      </VStack>
                    ) : (
                      <VStack>
                        <Text color="gray.500">
                          No delivery location selected
                        </Text>
                        <Button
                          colorScheme="green"
                          onClick={() => openStopForm('delivery')}
                        >
                          Add Delivery Location
                        </Button>
                      </VStack>
                    )}
                  </Box>
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
          </DrawerBody>

          <DrawerFooter>
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
          </DrawerFooter>
        </form>
      </DrawerContent>

      <StopForm
        isOpen={isStopFormOpen}
        onClose={handleStopFormClose}
        onSave={handleStopSave}
        stopType={editingStopType || 'pickup'}
        initialData={
          editingStopType
            ? formData[
                editingStopType === 'pickup' ? 'pickup_stop' : 'delivery_stop'
              ]
            : undefined
        }
      />
    </Drawer>
  )
}
