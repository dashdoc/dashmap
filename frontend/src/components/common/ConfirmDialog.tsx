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

interface ConfirmDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  confirmLabel?: string
  severity?: 'warning' | 'info'
  body?: React.ReactNode
  nameHighlight?: string
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  confirmLabel = 'Confirm',
  severity = 'warning',
  body,
  nameHighlight,
}) => (
  <Modal isOpen={isOpen} onClose={onClose}>
    <ModalOverlay />
    <ModalContent>
      <ModalHeader>{title}</ModalHeader>
      <ModalCloseButton />
      <ModalBody>
        <Alert status={severity} mb={4}>
          <AlertIcon />
          This action cannot be undone.
        </Alert>
        {body ?? (
          <Text>
            Are you sure you want to proceed
            {nameHighlight ? (
              <>
                {' '}
                with{' '}
                <Text as="span" fontWeight="bold">
                  {nameHighlight}
                </Text>
                ?
              </>
            ) : (
              '?'
            )}
          </Text>
        )}
      </ModalBody>
      <ModalFooter>
        <Button variant="ghost" mr={3} onClick={onClose}>
          Cancel
        </Button>
        <Button colorScheme="red" onClick={onConfirm}>
          {confirmLabel}
        </Button>
      </ModalFooter>
    </ModalContent>
  </Modal>
)
