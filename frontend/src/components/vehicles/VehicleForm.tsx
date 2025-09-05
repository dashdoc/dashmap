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
  SimpleGrid,
  Switch,
  FormHelperText,
} from '@chakra-ui/react'
import { post, put } from '../../lib/api'
import { useAuth } from '../../contexts/AuthContext'
import type { Vehicle } from '../../types/domain'

interface VehicleFormProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  vehicle?: Vehicle | null
}

export const VehicleForm: React.FC<VehicleFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  vehicle,
}) => {
  const [formData, setFormData] = useState({
    license_plate: '',
    make: '',
    model: '',
    year: new Date().getFullYear(),
    capacity: '',
    driver_name: '',
    driver_email: '',
    driver_phone: '',
    is_active: true,
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const { user } = useAuth()

  useEffect(() => {
    if (vehicle) {
      setFormData({
        license_plate: vehicle.license_plate,
        make: vehicle.make,
        model: vehicle.model,
        year: vehicle.year,
        capacity: vehicle.capacity,
        driver_name: vehicle.driver_name,
        driver_email: vehicle.driver_email,
        driver_phone: vehicle.driver_phone,
        is_active: vehicle.is_active,
      })
    } else {
      setFormData({
        license_plate: '',
        make: '',
        model: '',
        year: new Date().getFullYear(),
        capacity: '',
        driver_name: '',
        driver_email: '',
        driver_phone: '',
        is_active: true,
      })
    }
    setError('')
  }, [vehicle, isOpen])

  const handleChange =
    (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
      const value =
        field === 'year'
          ? parseInt(e.target.value) || 0
          : field === 'is_active'
            ? e.target.checked
            : e.target.value
      setFormData((prev) => ({
        ...prev,
        [field]: value,
      }))
    }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const vehicleData = {
        ...formData,
        company: user?.company_id,
      }

      if (vehicle) {
        await put(`/vehicles/${vehicle.id}/`, vehicleData)
      } else {
        await post('/vehicles/', vehicleData)
      }

      onSuccess()
    } catch (err) {
      const error = err as { response?: { data?: { error?: string } } }
      const errorMessage =
        error.response?.data?.error ||
        (vehicle ? 'Failed to update vehicle' : 'Failed to create vehicle')
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          {vehicle ? 'Edit Vehicle' : 'Add New Vehicle'}
        </ModalHeader>
        <ModalCloseButton />

        <form onSubmit={handleSubmit}>
          <ModalBody>
            <VStack spacing={4}>
              {error && (
                <Alert status="error">
                  <AlertIcon />
                  {error}
                </Alert>
              )}

              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} width="100%">
                <FormControl isRequired>
                  <FormLabel>License Plate</FormLabel>
                  <Input
                    type="text"
                    value={formData.license_plate}
                    onChange={handleChange('license_plate')}
                    placeholder="ABC123"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Make</FormLabel>
                  <Input
                    type="text"
                    value={formData.make}
                    onChange={handleChange('make')}
                    placeholder="Ford"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Model</FormLabel>
                  <Input
                    type="text"
                    value={formData.model}
                    onChange={handleChange('model')}
                    placeholder="Transit"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Year</FormLabel>
                  <Input
                    type="number"
                    value={formData.year}
                    onChange={handleChange('year')}
                    min="1900"
                    max={new Date().getFullYear() + 1}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Capacity</FormLabel>
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.capacity}
                    onChange={handleChange('capacity')}
                    placeholder="2.50"
                  />
                  <FormHelperText>Capacity in tons</FormHelperText>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Driver Name</FormLabel>
                  <Input
                    type="text"
                    value={formData.driver_name}
                    onChange={handleChange('driver_name')}
                    placeholder="John Doe"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Driver Email</FormLabel>
                  <Input
                    type="email"
                    value={formData.driver_email}
                    onChange={handleChange('driver_email')}
                    placeholder="john@example.com"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Driver Phone</FormLabel>
                  <Input
                    type="tel"
                    value={formData.driver_phone}
                    onChange={handleChange('driver_phone')}
                    placeholder="555-1234"
                  />
                </FormControl>
              </SimpleGrid>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="is_active" mb="0">
                  Active Status
                </FormLabel>
                <Switch
                  id="is_active"
                  isChecked={formData.is_active}
                  onChange={handleChange('is_active')}
                />
              </FormControl>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              type="submit"
              isLoading={isLoading}
              loadingText={vehicle ? 'Updating...' : 'Creating...'}
            >
              {vehicle ? 'Update Vehicle' : 'Create Vehicle'}
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  )
}
