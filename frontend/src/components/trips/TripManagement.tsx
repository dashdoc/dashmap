import React, { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Heading,
  HStack,
  Spinner,
  Alert,
  AlertIcon,
  useDisclosure,
  Badge,
  IconButton,
  Text,
} from '@chakra-ui/react'
import { AddIcon, EditIcon, DeleteIcon, ViewIcon } from '@chakra-ui/icons'
import { TripForm } from './TripForm'
import { DeleteConfirmModal } from './DeleteConfirmModal'
import { TripDetailsDrawer } from './TripDetailsDrawer'
import axios from 'axios'
import { useAuth } from '../../contexts/AuthContext'

interface Trip {
  id: number
  vehicle: number
  vehicle_license_plate: string
  dispatcher: number
  dispatcher_name: string
  name: string
  status: 'draft' | 'planned' | 'in_progress' | 'completed' | 'cancelled'
  planned_start_date: string
  planned_start_time: string
  actual_start_datetime?: string | null
  actual_end_datetime?: string | null
  notes: string
  driver_notified: boolean
  created_at: string
  updated_at: string
}

const API_BASE_URL = 'http://localhost:8000/api'

const getStatusColor = (status: Trip['status']) => {
  switch (status) {
    case 'draft':
      return 'gray'
    case 'planned':
      return 'blue'
    case 'in_progress':
      return 'yellow'
    case 'completed':
      return 'green'
    case 'cancelled':
      return 'red'
    default:
      return 'gray'
  }
}

export const TripManagement: React.FC = () => {
  const [trips, setTrips] = useState<Trip[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null)
  const [tripToDelete, setTripToDelete] = useState<Trip | null>(null)
  const [activeTrip, setActiveTrip] = useState<Trip | null>(null)

  const {
    isOpen: isFormOpen,
    onOpen: onFormOpen,
    onClose: onFormClose,
  } = useDisclosure()
  const {
    isOpen: isDeleteOpen,
    onOpen: onDeleteOpen,
    onClose: onDeleteClose,
  } = useDisclosure()
  const {
    isOpen: isDetailsOpen,
    onOpen: onDetailsOpen,
    onClose: onDetailsClose,
  } = useDisclosure()

  const { user } = useAuth()

  const fetchTrips = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/trips/`, {
        params: { company: user?.company_id },
      })
      setTrips(response.data.results || response.data)
      setError('')
    } catch (err) {
      setError('Failed to fetch trips. Please try again.')
      console.error('Error fetching trips:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user?.company_id) {
      fetchTrips()
    }
  }, [user])

  const handleCreateTrip = () => {
    setSelectedTrip(null)
    onFormOpen()
  }

  const handleEditTrip = (trip: Trip) => {
    setSelectedTrip(trip)
    onFormOpen()
  }

  const handleViewDetails = (trip: Trip) => {
    setActiveTrip(trip)
    onDetailsOpen()
  }

  const handleDeleteClick = (trip: Trip) => {
    setTripToDelete(trip)
    onDeleteOpen()
  }

  const handleDeleteConfirm = async () => {
    if (!tripToDelete) return

    try {
      await axios.delete(`${API_BASE_URL}/trips/${tripToDelete.id}/`)
      await fetchTrips()
      onDeleteClose()
      setTripToDelete(null)
    } catch (err) {
      console.error('Error deleting trip:', err)
      setError('Failed to delete trip. Please try again.')
    }
  }

  const handleFormSuccess = async () => {
    onFormClose()
    await fetchTrips()
  }

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
      </Box>
    )
  }

  return (
    <Box>
      <HStack justify="space-between" mb={6}>
        <Heading size="lg">Trip Management</Heading>
        <Button
          colorScheme="blue"
          leftIcon={<AddIcon />}
          onClick={handleCreateTrip}
        >
          Add Trip
        </Button>
      </HStack>

      {error && (
        <Alert status="error" mb={4}>
          <AlertIcon />
          {error}
        </Alert>
      )}

      {trips.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Text color="gray.500" fontSize="lg">
            No trips found. Click "Add Trip" to get started.
          </Text>
        </Box>
      ) : (
        <TableContainer>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Trip Name</Th>
                <Th>Vehicle</Th>
                <Th>Dispatcher</Th>
                <Th>Start Date/Time</Th>
                <Th>Status</Th>
                <Th>Notified</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {trips.map((trip) => (
                <Tr key={trip.id}>
                  <Td fontWeight="bold">{trip.name}</Td>
                  <Td>{trip.vehicle_license_plate}</Td>
                  <Td>{trip.dispatcher_name}</Td>
                  <Td>
                    <Box fontSize="sm">
                      <div>{trip.planned_start_date}</div>
                      <div>{trip.planned_start_time}</div>
                    </Box>
                  </Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(trip.status)}>
                      {trip.status.charAt(0).toUpperCase() +
                        trip.status.slice(1)}
                    </Badge>
                  </Td>
                  <Td>
                    <Badge
                      colorScheme={trip.driver_notified ? 'green' : 'gray'}
                    >
                      {trip.driver_notified ? 'Yes' : 'No'}
                    </Badge>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <IconButton
                        aria-label="View details"
                        icon={<ViewIcon />}
                        size="sm"
                        onClick={() => handleViewDetails(trip)}
                      />
                      <IconButton
                        aria-label="Edit trip"
                        icon={<EditIcon />}
                        size="sm"
                        onClick={() => handleEditTrip(trip)}
                      />
                      <IconButton
                        aria-label="Delete trip"
                        icon={<DeleteIcon />}
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        onClick={() => handleDeleteClick(trip)}
                      />
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      )}

      <TripForm
        isOpen={isFormOpen}
        onClose={onFormClose}
        onSuccess={handleFormSuccess}
        trip={selectedTrip}
      />

      <DeleteConfirmModal
        isOpen={isDeleteOpen}
        onClose={onDeleteClose}
        onConfirm={handleDeleteConfirm}
        tripName={tripToDelete ? tripToDelete.name : ''}
      />

      <TripDetailsDrawer
        isOpen={isDetailsOpen}
        onClose={onDetailsClose}
        trip={activeTrip}
        onTripUpdated={fetchTrips}
      />
    </Box>
  )
}
