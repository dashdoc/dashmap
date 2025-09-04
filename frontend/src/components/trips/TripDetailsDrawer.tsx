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
} from '@chakra-ui/react'
import { DeleteIcon } from '@chakra-ui/icons'
import { GripVertical } from 'lucide-react'
import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult,
} from '@hello-pangea/dnd'
import axios from 'axios'

interface Trip {
  id: number
  vehicle: number
  vehicle_license_plate: string
  name: string
  status: 'draft' | 'planned' | 'in_progress' | 'completed' | 'cancelled'
  planned_start_date: string
  planned_start_time: string
  notes: string
}

interface Stop {
  id: number
  name: string
  stop_type: 'loading' | 'unloading'
}

interface TripStop {
  id: number
  stop: Stop
  order: number
  planned_arrival_time: string
}

interface TripDetailsDrawerProps {
  isOpen: boolean
  onClose: () => void
  trip: Trip | null
  onTripUpdated: () => void
  onTripStopsChanged?: () => void
}

const API_BASE_URL = 'http://localhost:8000/api'

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
  const [stops, setStops] = useState<Stop[]>([])
  const [newStop, setNewStop] = useState({ stopId: '', time: '' })
  const [error, setError] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isAdding, setIsAdding] = useState(false)
  const [isReordering, setIsReordering] = useState(false)
  const toast = useToast()

  const fetchTripDetails = async () => {
    if (!trip) return
    try {
      const response = await axios.get(`${API_BASE_URL}/trips/${trip.id}/`)
      const data = response.data
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

  const fetchStops = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stops/`)
      setStops(response.data.results || response.data)
    } catch (err) {
      console.error('Error fetching stops:', err)
    }
  }

  useEffect(() => {
    if (isOpen && trip) {
      fetchTripDetails()
      fetchStops()
      setError('')
      setNewStop({ stopId: '', time: '' })
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
      await axios.put(`${API_BASE_URL}/trips/${trip.id}/`, {
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

  const handleAddStop = async () => {
    if (!trip || !newStop.stopId || !newStop.time) return
    setIsAdding(true)
    setError('')
    try {
      await axios.post(`${API_BASE_URL}/trip-stops/`, {
        trip: trip.id,
        stop: parseInt(newStop.stopId),
        order: tripStops.length + 1,
        planned_arrival_time: newStop.time,
      })
      await fetchTripDetails()
      setNewStop({ stopId: '', time: '' })
      // Notify the map to redraw the trip route
      if (onTripStopsChanged) {
        onTripStopsChanged()
      }
    } catch (err) {
      console.error('Error adding stop:', err)
      setError('Failed to add stop')
    } finally {
      setIsAdding(false)
    }
  }

  const handleDeleteStop = async (id: number) => {
    try {
      await axios.delete(`${API_BASE_URL}/trip-stops/${id}/`)
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
      await axios.post(`${API_BASE_URL}/trips/${trip.id}/reorder-stops/`, {
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

  const availableStops = stops.filter(
    (s) => !tripStops.some((ts) => ts.stop.id === s.id)
  )

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

              <HStack mt={4} spacing={2}>
                <Select
                  placeholder="Select stop"
                  value={newStop.stopId}
                  onChange={(e) =>
                    setNewStop((prev) => ({ ...prev, stopId: e.target.value }))
                  }
                >
                  {availableStops.map((stop) => (
                    <option key={stop.id} value={stop.id}>
                      {stop.name} ({stop.stop_type})
                    </option>
                  ))}
                </Select>
                <Input
                  type="time"
                  value={newStop.time}
                  onChange={(e) =>
                    setNewStop((prev) => ({ ...prev, time: e.target.value }))
                  }
                />
                <Button
                  colorScheme="blue"
                  onClick={handleAddStop}
                  isLoading={isAdding}
                  width="150px"
                >
                  Add Stop
                </Button>
              </HStack>
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
