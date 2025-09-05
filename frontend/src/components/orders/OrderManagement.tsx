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
  VStack,
} from '@chakra-ui/react'
import { AddIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons'
import { OrderForm } from './OrderForm'
import { ConfirmDialog } from '../common/ConfirmDialog'
import { get, post, del } from '../../lib/api'
import type { Order } from '../../types/domain'

export const OrderManagement: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [orderToDelete, setOrderToDelete] = useState<Order | null>(null)
  const [isGeneratingOrders, setIsGeneratingOrders] = useState(false)

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

  const fetchOrders = async () => {
    try {
      setLoading(true)
      const data = await get<Order[]>('/orders/')
      setOrders(data)
      setError('')
    } catch (err) {
      setError('Failed to fetch orders. Please try again.')
      console.error('Error fetching orders:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOrders()
  }, [])

  const handleCreateOrder = () => {
    setSelectedOrder(null)
    onFormOpen()
  }

  const handleEditOrder = (order: Order) => {
    setSelectedOrder(order)
    onFormOpen()
  }

  const handleDeleteClick = (order: Order) => {
    setOrderToDelete(order)
    onDeleteOpen()
  }

  const handleDeleteConfirm = async () => {
    if (!orderToDelete) return

    try {
      await del(`/orders/${orderToDelete.id}/`)
      await fetchOrders()
      onDeleteClose()
      setOrderToDelete(null)
    } catch (err) {
      console.error('Error deleting order:', err)
      setError('Failed to delete order. Please try again.')
    }
  }

  const handleFormSuccess = async () => {
    onFormClose()
    await fetchOrders()
  }

  const handleGenerateOrders = async () => {
    try {
      setIsGeneratingOrders(true)
      setError('')

      await post('/orders/generate-fake/')
      setError('')
      // Refresh the orders list to show new orders
      await fetchOrders()
    } catch (err) {
      console.error('Error generating orders:', err)
      setError('Failed to generate orders. Please try again.')
    } finally {
      setIsGeneratingOrders(false)
    }
  }

  const getStatusColor = (status: Order['status']) => {
    switch (status) {
      case 'pending':
        return 'orange'
      case 'assigned':
        return 'blue'
      case 'in_transit':
        return 'purple'
      case 'delivered':
        return 'green'
      case 'cancelled':
        return 'red'
      default:
        return 'gray'
    }
  }

  const getGoodsTypeColor = (type: Order['goods_type']) => {
    switch (type) {
      case 'fragile':
        return 'orange'
      case 'hazmat':
        return 'red'
      case 'refrigerated':
        return 'blue'
      case 'oversized':
        return 'purple'
      default:
        return 'gray'
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
        <Heading size="lg">Order Management</Heading>
        <HStack spacing={3}>
          <Button
            colorScheme="green"
            variant="outline"
            onClick={handleGenerateOrders}
            isLoading={isGeneratingOrders}
            loadingText="Generating..."
          >
            Generate Fake Orders
          </Button>
          <Button
            colorScheme="blue"
            leftIcon={<AddIcon />}
            onClick={handleCreateOrder}
          >
            Add Order
          </Button>
        </HStack>
      </HStack>

      {error && (
        <Alert status="error" mb={4}>
          <AlertIcon />
          {error}
        </Alert>
      )}

      {orders.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Text color="gray.500" fontSize="lg">
            No orders found. Click "Add Order" to get started.
          </Text>
        </Box>
      ) : (
        <TableContainer overflowX="auto">
          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                <Th minW="120px">Order #</Th>
                <Th minW="150px">Customer</Th>
                <Th minW="200px">Goods</Th>
                <Th minW="120px">Route</Th>
                <Th minW="100px">Type</Th>
                <Th minW="100px">Status</Th>
                <Th minW="120px" display={{ base: 'none', lg: 'table-cell' }}>
                  Weight/Volume
                </Th>
                <Th minW="100px">Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {orders.map((order) => (
                <Tr key={order.id}>
                  <Td fontWeight="bold" minW="120px">
                    {order.order_number}
                  </Td>
                  <Td minW="150px">
                    <VStack align="start" spacing={0}>
                      <Text fontWeight="medium">{order.customer_name}</Text>
                      <Text fontSize="sm" color="gray.500">
                        {order.customer_company}
                      </Text>
                    </VStack>
                  </Td>
                  <Td
                    minW="200px"
                    maxW="200px"
                    overflow="hidden"
                    textOverflow="ellipsis"
                    whiteSpace="nowrap"
                    title={order.goods_description}
                  >
                    {order.goods_description}
                  </Td>
                  <Td minW="120px">
                    <VStack align="start" spacing={0}>
                      <Text fontSize="sm">📍 {order.pickup_stop.name}</Text>
                      <Text fontSize="sm">🎯 {order.delivery_stop.name}</Text>
                    </VStack>
                  </Td>
                  <Td minW="100px">
                    <Badge
                      colorScheme={getGoodsTypeColor(order.goods_type)}
                      size="sm"
                    >
                      {order.goods_type}
                    </Badge>
                  </Td>
                  <Td minW="100px">
                    <Badge colorScheme={getStatusColor(order.status)} size="sm">
                      {order.status}
                    </Badge>
                  </Td>
                  <Td minW="120px" display={{ base: 'none', lg: 'table-cell' }}>
                    <VStack align="start" spacing={0}>
                      {order.goods_weight && (
                        <Text fontSize="sm">{order.goods_weight}kg</Text>
                      )}
                      {order.goods_volume && (
                        <Text fontSize="sm">{order.goods_volume}m³</Text>
                      )}
                    </VStack>
                  </Td>
                  <Td minW="100px">
                    <HStack spacing={1}>
                      <IconButton
                        aria-label="Edit order"
                        icon={<EditIcon />}
                        size="sm"
                        onClick={() => handleEditOrder(order)}
                      />
                      <IconButton
                        aria-label="Delete order"
                        icon={<DeleteIcon />}
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        onClick={() => handleDeleteClick(order)}
                      />
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      )}

      <OrderForm
        isOpen={isFormOpen}
        onClose={onFormClose}
        onSuccess={handleFormSuccess}
        order={selectedOrder}
      />

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={onDeleteClose}
        onConfirm={handleDeleteConfirm}
        title="Delete Order"
        confirmLabel="Delete Order"
        nameHighlight={orderToDelete?.order_number ?? ''}
      />
    </Box>
  )
}
