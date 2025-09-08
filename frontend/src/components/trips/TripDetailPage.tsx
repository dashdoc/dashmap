import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Badge,
  Card,
  CardBody,
  CardHeader,
  Spinner,
  Center,
  Alert,
  AlertIcon,
  Button,
  SimpleGrid,
  useDisclosure,
  Link,
} from '@chakra-ui/react'
import { ArrowLeft, Edit } from 'lucide-react'
import { Link as RouterLink } from 'react-router-dom'
import { get } from '../../lib/api'
import type { Trip, Order } from '../../types/domain'
import { TripDetailsDrawer } from './TripDetailsDrawer'

export const TripDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [trip, setTrip] = useState<Trip | null>(null)
  const [stopOrders, setStopOrders] = useState<{ [stopId: number]: Order[] }>(
    {}
  )
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const {
    isOpen: isEditOpen,
    onOpen: onEditOpen,
    onClose: onEditClose,
  } = useDisclosure()

  const fetchTrip = async () => {
    if (!id) return
    try {
      setLoading(true)
      const data = await get<Trip>(`/trips/${id}/`)
      setTrip(data)

      if (data.trip_stops && data.trip_stops.length > 0) {
        await fetchOrdersForStops(data)
      }
    } catch (err) {
      console.error('Error fetching trip:', err)
      setError('Failed to load trip details')
    } finally {
      setLoading(false)
    }
  }

  const fetchOrdersForStops = async (tripData: Trip) => {
    try {
      const orders = await get<Order[]>('/orders/')
      const stopOrderMap: { [stopId: number]: Order[] } = {}

      tripData.trip_stops?.forEach((tripStop) => {
        const stopId = tripStop.stop.id
        const relatedOrders = orders.filter(
          (order) =>
            order.pickup_stop.id === stopId || order.delivery_stop.id === stopId
        )
        if (relatedOrders.length > 0) {
          stopOrderMap[stopId] = relatedOrders
        }
      })

      setStopOrders(stopOrderMap)
    } catch (err) {
      console.error('Error fetching orders for stops:', err)
    }
  }

  useEffect(() => {
    fetchTrip()
  }, [id])

  const handleTripUpdated = () => {
    fetchTrip()
    onEditClose()
  }

  const getStatusColor = (status: Trip['status']) => {
    switch (status) {
      case 'draft':
        return 'gray'
      case 'planned':
        return 'blue'
      case 'in_progress':
        return 'orange'
      case 'completed':
        return 'green'
      case 'cancelled':
        return 'red'
      default:
        return 'gray'
    }
  }

  if (loading) {
    return (
      <Center h="400px">
        <Spinner size="xl" />
      </Center>
    )
  }

  if (error || !trip) {
    return (
      <Box p={6}>
        <Alert status="error">
          <AlertIcon />
          {error || 'Trip not found'}
        </Alert>
        <Button
          leftIcon={<ArrowLeft size={16} />}
          mt={4}
          onClick={() => navigate('/trips')}
        >
          Back to Trips
        </Button>
      </Box>
    )
  }

  return (
    <Box p={6}>
      <HStack justify="space-between" mb={6}>
        <HStack spacing={4}>
          <Button
            leftIcon={<ArrowLeft size={16} />}
            variant="ghost"
            onClick={() => navigate('/trips')}
          >
            Back
          </Button>
          <VStack align="start" spacing={0}>
            <Heading size="lg">{trip.name}</Heading>
            <Text color="gray.600" fontSize="sm">
              Created {new Date(trip.created_at).toLocaleDateString()}
            </Text>
          </VStack>
        </HStack>
        <HStack>
          <Badge colorScheme={getStatusColor(trip.status)} size="lg" p={2}>
            {trip.status.charAt(0).toUpperCase() + trip.status.slice(1)}
          </Badge>
          <Button
            leftIcon={<Edit size={16} />}
            colorScheme="blue"
            onClick={onEditOpen}
          >
            Edit Trip
          </Button>
        </HStack>
      </HStack>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Trip Information</Heading>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={3}>
              <Box>
                <Text fontSize="sm" color="gray.500">
                  Vehicle
                </Text>
                <Text fontWeight="bold">{trip.vehicle_license_plate}</Text>
              </Box>
              <Box>
                <Text fontSize="sm" color="gray.500">
                  Dispatcher
                </Text>
                <Text>{trip.dispatcher_name}</Text>
              </Box>
              <SimpleGrid columns={2} spacing={4} width="100%">
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Start Date
                  </Text>
                  <Text>
                    {new Date(trip.planned_start_date).toLocaleDateString()}
                  </Text>
                </Box>
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Start Time
                  </Text>
                  <Text>{trip.planned_start_time}</Text>
                </Box>
              </SimpleGrid>
              {trip.actual_start_datetime && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Actual Start
                  </Text>
                  <Text>
                    {new Date(trip.actual_start_datetime).toLocaleString()}
                  </Text>
                </Box>
              )}
              {trip.actual_end_datetime && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Actual End
                  </Text>
                  <Text>
                    {new Date(trip.actual_end_datetime).toLocaleString()}
                  </Text>
                </Box>
              )}
              {trip.notes && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Notes
                  </Text>
                  <Text>{trip.notes}</Text>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">
              Trip Stops ({trip.trip_stops?.length || 0})
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={4} maxH="400px" overflowY="auto">
              {trip.trip_stops && trip.trip_stops.length > 0 ? (
                trip.trip_stops.map((tripStop, index) => (
                  <Box
                    key={tripStop.id}
                    p={3}
                    border="1px"
                    borderColor="gray.200"
                    borderRadius="md"
                    width="100%"
                  >
                    <HStack justify="space-between" mb={2}>
                      <HStack>
                        <Box
                          minW="24px"
                          h="24px"
                          bg="blue.500"
                          color="white"
                          borderRadius="full"
                          display="flex"
                          alignItems="center"
                          justifyContent="center"
                          fontSize="sm"
                          fontWeight="bold"
                        >
                          {index + 1}
                        </Box>
                        <VStack align="start" spacing={0}>
                          <Text fontWeight="bold">{tripStop.stop.name}</Text>
                          <Text fontSize="sm" color="gray.600">
                            Arrival: {tripStop.planned_arrival_time}
                          </Text>
                        </VStack>
                      </HStack>
                      <Badge
                        colorScheme={
                          tripStop.stop.stop_type === 'pickup'
                            ? 'blue'
                            : 'green'
                        }
                        size="sm"
                      >
                        {tripStop.stop.stop_type}
                      </Badge>
                    </HStack>

                    {stopOrders[tripStop.stop.id] && (
                      <Box mt={2} pt={2} borderTop="1px" borderColor="gray.100">
                        <Text fontSize="xs" color="gray.500" mb={1}>
                          Related Orders:
                        </Text>
                        <VStack spacing={1} align="start">
                          {stopOrders[tripStop.stop.id].map((order) => (
                            <Link
                              key={order.id}
                              as={RouterLink}
                              to={`/orders/${order.id}`}
                              fontSize="xs"
                              color="blue.500"
                              _hover={{ textDecoration: 'underline' }}
                            >
                              #{order.order_number} - {order.customer_name}
                            </Link>
                          ))}
                        </VStack>
                      </Box>
                    )}

                    {tripStop.is_completed && (
                      <Badge colorScheme="green" size="sm" mt={2}>
                        Completed
                      </Badge>
                    )}
                  </Box>
                ))
              ) : (
                <Text color="gray.500">No stops added to this trip</Text>
              )}
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>

      <TripDetailsDrawer
        isOpen={isEditOpen}
        onClose={onEditClose}
        trip={trip}
        onTripUpdated={handleTripUpdated}
        onTripStopsChanged={fetchTrip}
      />
    </Box>
  )
}
