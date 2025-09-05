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
  Select,
  Textarea,
} from '@chakra-ui/react'
import { post, put } from '../../lib/api'
import type { Stop } from '../../types/domain'

interface StopFormProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  stop?: Stop | null
}

export const StopForm: React.FC<StopFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  stop,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    stop_type: 'loading' as 'loading' | 'unloading',
    contact_name: '',
    contact_phone: '',
    notes: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (stop) {
      setFormData({
        name: stop.name,
        address: stop.address,
        stop_type: stop.stop_type,
        contact_name: stop.contact_name,
        contact_phone: stop.contact_phone,
        notes: stop.notes,
      })
    } else {
      setFormData({
        name: '',
        address: '',
        stop_type: 'loading',
        contact_name: '',
        contact_phone: '',
        notes: '',
      })
    }
    setError('')
  }, [stop, isOpen])

  const handleChange =
    (field: string) =>
    (
      e: React.ChangeEvent<
        HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
      >
    ) => {
      setFormData((prev) => ({
        ...prev,
        [field]: e.target.value,
      }))
    }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      if (stop) {
        await put(`/stops/${stop.id}/`, formData)
      } else {
        await post('/stops/', formData)
      }

      onSuccess()
    } catch (err) {
      const error = err as { response?: { data?: { error?: string } } }
      const errorMessage =
        error.response?.data?.error ||
        (stop ? 'Failed to update stop' : 'Failed to create stop')
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{stop ? 'Edit Stop' : 'Add New Stop'}</ModalHeader>
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

              <FormControl isRequired>
                <FormLabel>Name</FormLabel>
                <Input
                  type="text"
                  value={formData.name}
                  onChange={handleChange('name')}
                  placeholder="Loading Dock A"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Address</FormLabel>
                <Textarea
                  value={formData.address}
                  onChange={handleChange('address')}
                  placeholder="100 Warehouse St, Industrial District"
                  rows={3}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Stop Type</FormLabel>
                <Select
                  value={formData.stop_type}
                  onChange={handleChange('stop_type')}
                >
                  <option value="loading">Loading</option>
                  <option value="unloading">Unloading</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Contact Name</FormLabel>
                <Input
                  type="text"
                  value={formData.contact_name}
                  onChange={handleChange('contact_name')}
                  placeholder="Dock Manager"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Contact Phone</FormLabel>
                <Input
                  type="tel"
                  value={formData.contact_phone}
                  onChange={handleChange('contact_phone')}
                  placeholder="555-0001"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Notes</FormLabel>
                <Textarea
                  value={formData.notes}
                  onChange={handleChange('notes')}
                  placeholder="Special instructions, access codes, etc."
                  rows={3}
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
              loadingText={stop ? 'Updating...' : 'Creating...'}
            >
              {stop ? 'Update Stop' : 'Create Stop'}
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  )
}
