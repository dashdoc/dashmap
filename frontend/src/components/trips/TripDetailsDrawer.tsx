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
    stopType: 'pickup' as 'pickup' | 'delivery',
    time: '',
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
      setNewOrder({ orderId: '', stopType: 'pickup', time: '' })
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
    if (!trip || !newOrder.orderId || !newOrder.time) return
    setIsAdding(true)
    setError('')
    try {
      const selectedOrder = orders?.find(
        (o) => o.id.toString() === newOrder.orderId
      )
      if (!selectedOrder) return

      // Determine which stop to add based on the selection
      const stop =
        newOrder.stopType === 'pickup'
          ? selectedOrder.pickup_stop
          : selectedOrder.delivery_stop

      await post('/trip-stops/', {
        trip: trip.id,
        stop: stop.id,
        order: tripStops.length + 1,
        planned_arrival_time: newOrder.time,
      })

      // Update order status to assigned
      await put(`/orders/${selectedOrder.id}/`, {
        ...selectedOrder,
        status: 'assigned',
      })

      await fetchTripDetails()
      await fetchAvailableOrders() // Refresh to remove the now-assigned order
      setNewOrder({ orderId: '', stopType: 'pickup', time: '' })

      // Notify the map to redraw the trip route
      if (onTripStopsChanged) {
        onTripStopsChanged()
      }
    } catch (err) {
      console.error('Error adding order:', err)
      setError('Failed to add order')
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
    const [removed] = reorderedStops.splice(sourceIndex, 1)
    reorderedStops.splice(destinationIndex, 0, removed)

    // Update local state immediately for better UX
    setTripStops(reorderedStops)

    try {
      setIsReordering(true)

      // Create the orders array for the API call
      const orders = reorderedStops.map((stop, index) => ({
        id: stop.id,
        order: index + 1, // API expects 1-based ordering
      }))

      // Call the reorder API
      await post(`/trips/${trip.id}/reorder-stops/`, {
        orders,
      })

      // Refresh trip details to ensure we have the latest data
      await fetchTripDetails()

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
      setError('Failed to reorder stops')
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
                                    {ts.orders && ts.orders.length > 0 && (
                                      <Box fontSize="sm" mt={1}>
                                        <Text
                                          color="blue.600"
                                          fontWeight="medium"
                                        >
                                          Orders:
                                        </Text>
                                        {ts.orders.map((order) => (
                                          <Link
                                            key={order.id}
                                            as={RouterLink}
                                            to={`/orders/${order.id}`}
                                            color="blue.500"
                                            fontSize="sm"
                                            textDecoration="underline"
                                            mr={2}
                                          >
                                            {order.order_number}
                                          </Link>
                                        ))}
                                      </Box>
                                    )}
                                  </Box>
                                  <Badge
                                    colorScheme={
                                      ts.stop.stop_type === 'loading'
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
                <HStack spacing={2}>
                  <Select
                    placeholder="Select order"
                    value={newOrder.orderId}
                    onChange={(e) =>
                      setNewOrder((prev) => ({
                        ...prev,
                        orderId: e.target.value,
                      }))
                    }
                    flex={2}
                  >
                    {availableOrders?.map((order) => (
                      <option key={order.id} value={order.id}>
                        {order.order_number} - {order.customer_name}
                      </option>
                    ))}
                  </Select>
                  <Select
                    value={newOrder.stopType}
                    onChange={(e) =>
                      setNewOrder((prev) => ({
                        ...prev,
                        stopType: e.target.value as 'pickup' | 'delivery',
                      }))
                    }
                    flex={1}
                  >
                    <option value="pickup">Pickup</option>
                    <option value="delivery">Delivery</option>
                  </Select>
                </HStack>
                <HStack spacing={2}>
                  <Input
                    type="time"
                    value={newOrder.time}
                    onChange={(e) =>
                      setNewOrder((prev) => ({ ...prev, time: e.target.value }))
                    }
                    placeholder="Arrival time"
                    flex={1}
                  />
                  <Button
                    colorScheme="blue"
                    onClick={handleAddOrder}
                    isLoading={isAdding}
                    width="150px"
                  >
                    Add to Trip
                  </Button>
                </HStack>
                {newOrder.orderId && (
                  <Box p={2} bg="gray.50" borderRadius="md" fontSize="sm">
                    {(() => {
                      const selectedOrder = orders?.find(
                        (o) => o.id.toString() === newOrder.orderId
                      )
                      if (!selectedOrder) return null
                      const stop =
                        newOrder.stopType === 'pickup'
                          ? selectedOrder.pickup_stop
                          : selectedOrder.delivery_stop
                      return (
                        <Text>
                          <Text as="span" fontWeight="medium">
                            {newOrder.stopType === 'pickup'
                              ? 'Pickup'
                              : 'Delivery'}{' '}
                            Location:
                          </Text>{' '}
                          {stop.name} - {stop.address}
                        </Text>
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
