import React, { useState, useEffect } from 'react'
import {
  Box,
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
import { EditIcon, DeleteIcon } from '@chakra-ui/icons'
import { ConfirmDialog } from '../common/ConfirmDialog'
import { TripDetailsDrawer } from './TripDetailsDrawer'
import { get, del } from '../../lib/api'
import { useAuth } from '../../contexts/AuthContext'
import type { Trip } from '../../types/domain'

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
  const [tripToDelete, setTripToDelete] = useState<Trip | null>(null)
  const [activeTrip, setActiveTrip] = useState<Trip | null>(null)

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
      const data = await get<Trip[]>('/trips/', { company: user?.company_id })
      setTrips(data)
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

  const handleEditTrip = (trip: Trip) => {
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
      await del(`/trips/${tripToDelete.id}/`)
      await fetchTrips()
      onDeleteClose()
      setTripToDelete(null)
    } catch (err) {
      console.error('Error deleting trip:', err)
      setError('Failed to delete trip. Please try again.')
    }
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
      <Heading size="lg" mb={6}>
        Trip Management
      </Heading>

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

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={onDeleteClose}
        onConfirm={handleDeleteConfirm}
        title="Delete Trip"
        confirmLabel="Delete Trip"
        nameHighlight={tripToDelete?.name ?? ''}
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
