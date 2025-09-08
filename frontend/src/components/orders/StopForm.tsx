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
  SimpleGrid,
} from '@chakra-ui/react'

interface StopData {
  id?: number
  name: string
  address: string
  contact_name: string
  contact_phone: string
  notes: string
}

interface StopFormProps {
  isOpen: boolean
  onClose: () => void
  onSave: (stopData: StopData) => void
  stopType: 'pickup' | 'delivery'
  initialData?: StopData
}

export const StopForm: React.FC<StopFormProps> = ({
  isOpen,
  onClose,
  onSave,
  stopType,
  initialData,
}) => {
  const [formData, setFormData] = useState<StopData>({
    id: undefined,
    name: '',
    address: '',
    contact_name: '',
    contact_phone: '',
    notes: '',
  })

  useEffect(() => {
    if (initialData) {
      setFormData(initialData)
    } else {
      setFormData({
        id: undefined,
        name: '',
        address: '',
        contact_name: '',
        contact_phone: '',
        notes: '',
      })
    }
  }, [initialData, isOpen])

  const handleChange =
    (field: keyof StopData) => (e: React.ChangeEvent<HTMLInputElement>) => {
      setFormData((prev) => ({
        ...prev,
        [field]: e.target.value,
      }))
    }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
    onClose()
  }

  const title = stopType === 'pickup' ? 'Pickup Location' : 'Delivery Location'
  const colorScheme = stopType === 'pickup' ? 'blue' : 'green'

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <form onSubmit={handleSubmit}>
          <ModalHeader color={`${colorScheme}.600`}>{title}</ModalHeader>
          <ModalCloseButton />

          <ModalBody>
            <VStack spacing={4} align="stretch">
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Name</FormLabel>
                  <Input
                    value={formData.name}
                    onChange={handleChange('name')}
                    placeholder={`${title} name`}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Address</FormLabel>
                  <Input
                    value={formData.address}
                    onChange={handleChange('address')}
                    placeholder="Full address"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Contact Name</FormLabel>
                  <Input
                    value={formData.contact_name}
                    onChange={handleChange('contact_name')}
                    placeholder="Contact person"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Contact Phone</FormLabel>
                  <Input
                    value={formData.contact_phone}
                    onChange={handleChange('contact_phone')}
                    placeholder="Phone number"
                  />
                </FormControl>
              </SimpleGrid>

              <FormControl>
                <FormLabel>Notes</FormLabel>
                <Input
                  value={formData.notes}
                  onChange={handleChange('notes')}
                  placeholder={`Special instructions for ${stopType}`}
                />
              </FormControl>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              type="submit"
              colorScheme={colorScheme}
              isDisabled={!formData.name || !formData.address}
            >
              Save {title}
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  )
}
