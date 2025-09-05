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
import { VehicleForm } from './VehicleForm'
import { ConfirmDialog } from '../common/ConfirmDialog'
import { get, del } from '../../lib/api'
import { useAuth } from '../../contexts/AuthContext'
import type { Vehicle } from '../../types/domain'

export const VehicleManagement: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null)
  const [vehicleToDelete, setVehicleToDelete] = useState<Vehicle | null>(null)

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

  const { user } = useAuth()

  const fetchVehicles = async () => {
    try {
      setLoading(true)
      const data = await get<Vehicle[]>('/vehicles/', {
        company: user?.company_id,
      })
      setVehicles(data)
      setError('')
    } catch (err) {
      setError('Failed to fetch vehicles. Please try again.')
      console.error('Error fetching vehicles:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user?.company_id) {
      fetchVehicles()
    }
  }, [user])

  const handleCreateVehicle = () => {
    setSelectedVehicle(null)
    onFormOpen()
  }

  const handleEditVehicle = (vehicle: Vehicle) => {
    setSelectedVehicle(vehicle)
    onFormOpen()
  }

  const handleDeleteClick = (vehicle: Vehicle) => {
    setVehicleToDelete(vehicle)
    onDeleteOpen()
  }

  const handleDeleteConfirm = async () => {
    if (!vehicleToDelete) return

    try {
      await del(`/vehicles/${vehicleToDelete.id}/`)
      await fetchVehicles()
      onDeleteClose()
      setVehicleToDelete(null)
    } catch (err) {
      console.error('Error deleting vehicle:', err)
      setError('Failed to delete vehicle. Please try again.')
    }
  }

  const handleFormSuccess = async () => {
    onFormClose()
    await fetchVehicles()
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
        <Heading size="lg">Vehicle Management</Heading>
        <Button
          colorScheme="blue"
          leftIcon={<AddIcon />}
          onClick={handleCreateVehicle}
        >
          Add Vehicle
        </Button>
      </HStack>

      {error && (
        <Alert status="error" mb={4}>
          <AlertIcon />
          {error}
        </Alert>
      )}

      {vehicles.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Text color="gray.500" fontSize="lg">
            No vehicles found. Click "Add Vehicle" to get started.
          </Text>
        </Box>
      ) : (
        <TableContainer>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>License Plate</Th>
                <Th>Vehicle</Th>
                <Th>Driver</Th>
                <Th>Contact</Th>
                <Th>Capacity</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {vehicles.map((vehicle) => (
                <Tr key={vehicle.id}>
                  <Td fontWeight="bold">{vehicle.license_plate}</Td>
                  <Td>
                    {vehicle.year} {vehicle.make} {vehicle.model}
                  </Td>
                  <Td>{vehicle.driver_name}</Td>
                  <Td>
                    <Box fontSize="sm">
                      <div>{vehicle.driver_email}</div>
                      <div>{vehicle.driver_phone}</div>
                    </Box>
                  </Td>
                  <Td>{vehicle.capacity} tons</Td>
                  <Td>
                    <Badge colorScheme={vehicle.is_active ? 'green' : 'red'}>
                      {vehicle.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <IconButton
                        aria-label="Edit vehicle"
                        icon={<EditIcon />}
                        size="sm"
                        onClick={() => handleEditVehicle(vehicle)}
                      />
                      <IconButton
                        aria-label="Delete vehicle"
                        icon={<DeleteIcon />}
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        onClick={() => handleDeleteClick(vehicle)}
                      />
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      )}

      <VehicleForm
        isOpen={isFormOpen}
        onClose={onFormClose}
        onSuccess={handleFormSuccess}
        vehicle={selectedVehicle}
      />

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={onDeleteClose}
        onConfirm={handleDeleteConfirm}
        title="Delete Vehicle"
        confirmLabel="Delete Vehicle"
        nameHighlight={
          vehicleToDelete
            ? `${vehicleToDelete.license_plate} - ${vehicleToDelete.make} ${vehicleToDelete.model}`
            : ''
        }
      />
    </Box>
  )
}
