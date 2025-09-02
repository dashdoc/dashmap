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
import { AddIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons'
import { StopForm } from './StopForm'
import { DeleteConfirmModal } from './DeleteConfirmModal'
import axios from 'axios'

interface Stop {
  id: number
  name: string
  address: string
  stop_type: 'loading' | 'unloading'
  contact_name: string
  contact_phone: string
  notes: string
  created_at: string
  updated_at: string
}

const API_BASE_URL = 'http://localhost:8000/api'

export const StopManagement: React.FC = () => {
  const [stops, setStops] = useState<Stop[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [selectedStop, setSelectedStop] = useState<Stop | null>(null)
  const [stopToDelete, setStopToDelete] = useState<Stop | null>(null)
  const [isGettingOrders, setIsGettingOrders] = useState(false)

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

  const fetchStops = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/stops/`)
      setStops(response.data.results || response.data)
      setError('')
    } catch (err) {
      setError('Failed to fetch stops. Please try again.')
      console.error('Error fetching stops:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStops()
  }, [])

  const handleCreateStop = () => {
    setSelectedStop(null)
    onFormOpen()
  }

  const handleEditStop = (stop: Stop) => {
    setSelectedStop(stop)
    onFormOpen()
  }

  const handleDeleteClick = (stop: Stop) => {
    setStopToDelete(stop)
    onDeleteOpen()
  }

  const handleDeleteConfirm = async () => {
    if (!stopToDelete) return

    try {
      await axios.delete(`${API_BASE_URL}/stops/${stopToDelete.id}/`)
      await fetchStops()
      onDeleteClose()
      setStopToDelete(null)
    } catch (err) {
      console.error('Error deleting stop:', err)
      setError('Failed to delete stop. Please try again.')
    }
  }

  const handleFormSuccess = async () => {
    onFormClose()
    await fetchStops()
  }

  const handleGetOrders = async () => {
    try {
      setIsGettingOrders(true)
      setError('')

      const response = await axios.post(`${API_BASE_URL}/stops/get-orders/`)

      if (response.status === 201) {
        setError('')
        // Refresh the stops list to show new orders
        await fetchStops()
      }
    } catch (err) {
      console.error('Error getting orders:', err)
      setError('Failed to get orders. Please try again.')
    } finally {
      setIsGettingOrders(false)
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
      <HStack justify="space-between" mb={6}>
        <Heading size="lg">Stop Management</Heading>
        <HStack spacing={3}>
          <Button
            colorScheme="green"
            variant="outline"
            onClick={handleGetOrders}
            isLoading={isGettingOrders}
            loadingText="Getting Orders..."
          >
            Get Orders
          </Button>
          <Button
            colorScheme="blue"
            leftIcon={<AddIcon />}
            onClick={handleCreateStop}
          >
            Add Stop
          </Button>
        </HStack>
      </HStack>

      {error && (
        <Alert status="error" mb={4}>
          <AlertIcon />
          {error}
        </Alert>
      )}

      {stops.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Text color="gray.500" fontSize="lg">
            No stops found. Click "Add Stop" to get started.
          </Text>
        </Box>
      ) : (
        <TableContainer>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Address</Th>
                <Th>Type</Th>
                <Th>Contact</Th>
                <Th>Phone</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {stops.map((stop) => (
                <Tr key={stop.id}>
                  <Td fontWeight="bold">{stop.name}</Td>
                  <Td>{stop.address}</Td>
                  <Td>
                    <Badge
                      colorScheme={
                        stop.stop_type === 'loading' ? 'blue' : 'green'
                      }
                    >
                      {stop.stop_type === 'loading' ? 'Loading' : 'Unloading'}
                    </Badge>
                  </Td>
                  <Td>{stop.contact_name}</Td>
                  <Td>{stop.contact_phone}</Td>
                  <Td>
                    <HStack spacing={2}>
                      <IconButton
                        aria-label="Edit stop"
                        icon={<EditIcon />}
                        size="sm"
                        onClick={() => handleEditStop(stop)}
                      />
                      <IconButton
                        aria-label="Delete stop"
                        icon={<DeleteIcon />}
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        onClick={() => handleDeleteClick(stop)}
                      />
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      )}

      <StopForm
        isOpen={isFormOpen}
        onClose={onFormClose}
        onSuccess={handleFormSuccess}
        stop={selectedStop}
      />

      <DeleteConfirmModal
        isOpen={isDeleteOpen}
        onClose={onDeleteClose}
        onConfirm={handleDeleteConfirm}
        stopName={stopToDelete ? stopToDelete.name : ''}
      />
    </Box>
  )
}
