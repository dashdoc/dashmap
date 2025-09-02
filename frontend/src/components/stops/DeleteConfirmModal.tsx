import React from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  Text,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'

interface DeleteConfirmModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  stopName: string
}

export const DeleteConfirmModal: React.FC<DeleteConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  stopName,
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Delete Stop</ModalHeader>
        <ModalCloseButton />

        <ModalBody>
          <Alert status="warning" mb={4}>
            <AlertIcon />
            This action cannot be undone.
          </Alert>

          <Text>
            Are you sure you want to delete the stop{' '}
            <Text as="span" fontWeight="bold">
              {stopName}
            </Text>
            ?
          </Text>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="red" onClick={onConfirm}>
            Delete Stop
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
