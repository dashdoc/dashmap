import React, { useEffect, useState } from 'react'
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
  Select,
  Textarea,
  VStack,
  Box,
  Heading,
  HStack,
  IconButton,
  Alert,
  Flex,
  AlertIcon,
  Badge,
  useToast,
  Link,
  Text,
} from '@chakra-ui/react'
import { DeleteIcon } from '@chakra-ui/icons'
import { GripVertical } from 'lucide-react'
import {
  DragDropContext,
  Droppable,
  Draggable,
  type DropResult,
} from '@hello-pangea/dnd'
import { Link as RouterLink } from 'react-router-dom'
import { get, put, post, del } from '../../lib/api'
import type { Trip, Order, TripStop } from '../../types/domain'

interface TripDetailsDrawerProps {
  isOpen: boolean
  onClose: () => void
  trip: Trip | null
  onTripUpdated: () => void
  onTripStopsChanged?: () => void
}

export const TripDetailsDrawer: React.FC<TripDetailsDrawerProps> = ({
  isOpen,
  onClose,
  trip,
  onTripUpdated,
  onTripStopsChanged,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    vehicle: '',
    status: 'draft' as Trip['status'],
    planned_start_date: '',
    planned_start_time: '',
    notes: '',
  })
  const [tripStops, setTripStops] = useState<TripStop[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [newOrder, setNewOrder] = useState({
    orderId: '',
    pickupTime: '',
    deliveryTime: '',
  })
  const [error, setError] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isAdding, setIsAdding] = useState(false)
  const [isReordering, setIsReordering] = useState(false)
  const toast = useToast()

  const fetchTripDetails = async () => {
    if (!trip) return
    try {
      const data = await get<Trip>(`/trips/${trip.id}/`)
      setFormData({
        name: data.name,
        vehicle: data.vehicle.toString(),
        status: data.status,
        planned_start_date: data.planned_start_date,
        planned_start_time: data.planned_start_time,
        notes: data.notes || '',
      })
      setTripStops(data.trip_stops || [])
    } catch (err) {
      console.error('Error fetching trip details:', err)
    }
  }

  const fetchAvailableOrders = async () => {
    try {
      const data = await get<Order[]>('/orders/?available_for_trip=true')
      setOrders(data)
    } catch (err) {
      console.error('Error fetching orders:', err)
    }
  }

  useEffect(() => {
    if (isOpen && trip) {
      fetchTripDetails()
      fetchAvailableOrders()
      setError('')
      setNewOrder({ orderId: '', pickupTime: '', deliveryTime: '' })
    }
  }, [isOpen, trip])

  const handleChange =
    (field: string) =>
    (
      e: React.ChangeEvent<
        HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
      >
    ) => {
      setFormData((prev) => ({ ...prev, [field]: e.target.value }))
    }

  const handleSave = async () => {
    if (!trip) return
    setIsSaving(true)
    setError('')
    try {
      await put(`/trips/${trip.id}/`, {
        ...formData,
        vehicle: parseInt(formData.vehicle),
      })
      onTripUpdated()
      onClose()
    } catch (err) {
      const errorMessage =
        (err as { response?: { data?: { error?: string } } }).response?.data
          ?.error || 'Failed to update trip'
      setError(errorMessage)
    } finally {
      setIsSaving(false)
    }
  }

  const handleAddOrder = async () => {
    if (
      !trip ||
      !newOrder.orderId ||
      !newOrder.pickupTime ||
      !newOrder.deliveryTime
    )
      return
    setIsAdding(true)
    setError('')
    try {
      const selectedOrder = orders?.find(
        (o) => o.id.toString() === newOrder.orderId
      )
      if (!selectedOrder) return

      // Use the new add-order endpoint to add both pickup and delivery stops
      await post(`/trips/${trip.id}/add-order/`, {
        order: parseInt(newOrder.orderId),
        pickup_time: newOrder.pickupTime,
        delivery_time: newOrder.deliveryTime,
      })

      // Update order status to assigned
      await put(`/orders/${selectedOrder.id}/`, {
        ...selectedOrder,
        status: 'assigned',
      })

      await fetchTripDetails()
      await fetchAvailableOrders() // Refresh to remove the now-assigned order
      setNewOrder({ orderId: '', pickupTime: '', deliveryTime: '' })

      toast({
        title: 'Order added',
        description: `Complete order (pickup + delivery) added to trip.`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })

      // Notify the map to redraw the trip route
      if (onTripStopsChanged) {
        onTripStopsChanged()
      }
    } catch (err) {
      console.error('Error adding order:', err)
      const errorMessage =
        (err as { response?: { data?: { error?: string } } }).response?.data
          ?.error || 'Failed to add order'
      setError(errorMessage)
    } finally {
      setIsAdding(false)
    }
  }

  const handleDeleteStop = async (id: number) => {
    try {
      await del(`/trip-stops/${id}/`)
      await fetchTripDetails()
      toast({
        title: 'Stop removed',
        description: 'The stop has been removed from the trip.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      // Notify the map to redraw the trip route
      if (onTripStopsChanged) {
        onTripStopsChanged()
      }
    } catch (err) {
      console.error('Error deleting stop:', err)
      setError('Failed to delete stop')
    }
  }

  const handleDragEnd = async (result: DropResult) => {
    if (!result.destination || !trip) return

    const sourceIndex = result.source.index
    const destinationIndex = result.destination.index

    if (sourceIndex === destinationIndex) return

    // Create a copy of the trip stops array
    const reorderedStops = Array.from(tripStops)
    const removed = reorderedStops.splice(sourceIndex, 2)
    reorderedStops.splice(destinationIndex, 0, removed[1])

    // Update local state immediately for better UX
    setTripStops(reorderedStops)

    try {
      setIsReordering(true)

      // Create the sequences array for the API call
      const sequences = reorderedStops.map((stop, index) => ({
        id: stop.id,
        sequence: index,
      }))

      // Call the reorder API
      const stops: TripStop[] = await post(`/trips/${trip.id}/reorder-stops/`, {
        sequences,
      })
      setTripStops(stops)

      toast({
        title: 'Stops reordered',
        description: 'The trip stops have been reordered successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      // Notify the map to redraw the trip route
      if (onTripStopsChanged) {
        onTripStopsChanged()
      }
    } catch (err) {
      console.error('Error reordering stops:', err)

      // Revert to original order on error
      await fetchTripDetails()
    } finally {
      setIsReordering(false)
    }
  }

  // Orders are already filtered by the backend
  const availableOrders = orders || []

  return (
    <Drawer isOpen={isOpen} placement="right" onClose={onClose} size="xl">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>Trip Details</DrawerHeader>

        <DrawerBody>
          <VStack spacing={4} align="stretch">
            {error && (
              <Alert status="error">
                <AlertIcon />
                {error}
              </Alert>
            )}

            <FormControl>
              <FormLabel>Trip Name</FormLabel>
              <Input value={formData.name} onChange={handleChange('name')} />
            </FormControl>

            <FormControl>
              <FormLabel>Vehicle</FormLabel>
              <Input value={trip?.vehicle_license_plate || ''} isDisabled />
            </FormControl>

            <FormControl>
              <FormLabel>Status</FormLabel>
              <Select value={formData.status} onChange={handleChange('status')}>
                <option value="draft">Draft</option>
                <option value="planned">Planned</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </Select>
            </FormControl>

            <HStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Start Date</FormLabel>
                <Input
                  type="date"
                  value={formData.planned_start_date}
                  onChange={handleChange('planned_start_date')}
                />
              </FormControl>
              <FormControl>
                <FormLabel>Start Time</FormLabel>
                <Input
                  type="time"
                  value={formData.planned_start_time}
                  onChange={handleChange('planned_start_time')}
                />
              </FormControl>
            </HStack>

            <FormControl>
              <FormLabel>Notes</FormLabel>
              <Textarea
                value={formData.notes}
                onChange={handleChange('notes')}
                rows={3}
              />
            </FormControl>

            <Box mt={4}>
              <Heading size="md" mb={2}>
                Stops
                {isReordering && (
                  <Box as="span" ml={2} fontSize="sm" color="blue.500">
                    Reordering...
                  </Box>
                )}
              </Heading>
              {tripStops.length === 0 ? (
                <Box>No stops added.</Box>
              ) : (
                <DragDropContext onDragEnd={handleDragEnd}>
                  <Droppable droppableId="trip-stops">
                    {(provided) => (
                      <Box
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                        border="1px"
                        borderColor="gray.200"
                        borderRadius="md"
                      >
                        {tripStops.map((ts, index) => (
                          <Draggable
                            key={ts.id}
                            draggableId={ts.id.toString()}
                            index={index}
                          >
                            {(provided, snapshot) => (
                              <Box
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                borderBottom={
                                  index < tripStops.length - 1
                                    ? '1px solid'
                                    : 'none'
                                }
                                borderColor="gray.100"
                                bg={snapshot.isDragging ? 'blue.50' : 'white'}
                                p={3}
                                _hover={{ bg: 'gray.50' }}
                                transition="background-color 0.2s"
                              >
                                <HStack spacing={3}>
                                  <Box
                                    {...provided.dragHandleProps}
                                    cursor="grab"
                                    _active={{ cursor: 'grabbing' }}
                                    display="flex"
                                    alignItems="center"
                                    color="gray.400"
                                    _hover={{ color: 'gray.600' }}
                                  >
                                    <GripVertical size={16} />
                                  </Box>
                                  <Box
                                    minW="24px"
                                    textAlign="center"
                                    fontWeight="bold"
                                    color="blue.600"
                                    fontSize="sm"
                                  >
                                    {index + 1}
                                  </Box>
                                  <Box flex="1">
                                    <Box fontWeight="medium">
                                      {ts.stop.name}
                                    </Box>
                                    <Box fontSize="sm" color="gray.600" mt={1}>
                                      Arrival: {ts.planned_arrival_time}
                                    </Box>
                                    {ts.linked_order && (
                                      <Flex fontSize="sm" mt={1}>
                                        <Link
                                          as={RouterLink}
                                          to={`/orders/${ts.linked_order.id}`}
                                          color="blue.500"
                                          fontSize="sm"
                                          textDecoration="underline"
                                          mr={2}
                                        >
                                          {ts.linked_order.order_number}
                                        </Link>
                                      </Flex>
                                    )}
                                  </Box>
                                  <Badge
                                    colorScheme={
                                      ts.stop.stop_type === 'pickup'
                                        ? 'blue'
                                        : 'green'
                                    }
                                    size="sm"
                                  >
                                    {ts.stop.stop_type}
                                  </Badge>
                                  <IconButton
                                    aria-label="Remove stop"
                                    icon={<DeleteIcon />}
                                    size="sm"
                                    variant="ghost"
                                    colorScheme="red"
                                    onClick={() => handleDeleteStop(ts.id)}
                                  />
                                </HStack>
                              </Box>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                      </Box>
                    )}
                  </Droppable>
                </DragDropContext>
              )}

              <VStack mt={4} spacing={3} align="stretch">
                <Select
                  placeholder="Select order to add to trip"
                  value={newOrder.orderId}
                  onChange={(e) =>
                    setNewOrder((prev) => ({
                      ...prev,
                      orderId: e.target.value,
                    }))
                  }
                >
                  {availableOrders?.map((order) => (
                    <option key={order.id} value={order.id}>
                      {order.order_number} - {order.customer_name}
                    </option>
                  ))}
                </Select>
                <HStack spacing={2}>
                  <Box flex={1}>
                    <Text fontSize="sm" color="gray.600" mb={1}>
                      Pickup Time
                    </Text>
                    <Input
                      type="time"
                      value={newOrder.pickupTime}
                      onChange={(e) =>
                        setNewOrder((prev) => ({
                          ...prev,
                          pickupTime: e.target.value,
                        }))
                      }
                      placeholder="Pickup time"
                    />
                  </Box>
                  <Box flex={1}>
                    <Text fontSize="sm" color="gray.600" mb={1}>
                      Delivery Time
                    </Text>
                    <Input
                      type="time"
                      value={newOrder.deliveryTime}
                      onChange={(e) =>
                        setNewOrder((prev) => ({
                          ...prev,
                          deliveryTime: e.target.value,
                        }))
                      }
                      placeholder="Delivery time"
                    />
                  </Box>
                  <Button
                    colorScheme="blue"
                    onClick={handleAddOrder}
                    isLoading={isAdding}
                    width="150px"
                    mt={6}
                  >
                    Add Order
                  </Button>
                </HStack>
                {newOrder.orderId && (
                  <Box p={3} bg="gray.50" borderRadius="md" fontSize="sm">
                    {(() => {
                      const selectedOrder = orders?.find(
                        (o) => o.id.toString() === newOrder.orderId
                      )
                      if (!selectedOrder) return null
                      return (
                        <VStack spacing={2} align="stretch">
                          <Text fontWeight="medium" color="blue.600">
                            Order: {selectedOrder.order_number}
                          </Text>
                          <Box>
                            <Text fontWeight="medium" color="green.600">
                              📦 Pickup:
                            </Text>
                            <Text>
                              {selectedOrder.pickup_stop?.name} -{' '}
                              {selectedOrder.pickup_stop?.address}
                            </Text>
                          </Box>
                          <Box>
                            <Text fontWeight="medium" color="purple.600">
                              🚚 Delivery:
                            </Text>
                            <Text>
                              {selectedOrder.delivery_stop?.name} -{' '}
                              {selectedOrder.delivery_stop?.address}
                            </Text>
                          </Box>
                        </VStack>
                      )
                    })()}
                  </Box>
                )}
              </VStack>
            </Box>
          </VStack>
        </DrawerBody>

        <DrawerFooter>
          <Button variant="outline" mr={3} onClick={onClose}>
            Close
          </Button>
          <Button colorScheme="blue" onClick={handleSave} isLoading={isSaving}>
            Save Changes
          </Button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  )
}
