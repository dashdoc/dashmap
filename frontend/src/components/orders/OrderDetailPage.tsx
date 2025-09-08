import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Badge,
  Card,
  CardBody,
  CardHeader,
  Spinner,
  Center,
  Alert,
  AlertIcon,
  Button,
  SimpleGrid,
  useDisclosure,
} from '@chakra-ui/react'
import { ArrowLeft, Edit } from 'lucide-react'
import { get } from '../../lib/api'
import type { Order } from '../../types/domain'
import { OrderForm } from './OrderForm'

export const OrderDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const {
    isOpen: isEditOpen,
    onOpen: onEditOpen,
    onClose: onEditClose,
  } = useDisclosure()

  const fetchOrder = async () => {
    if (!id) return
    try {
      setLoading(true)
      const data = await get<Order>(`/orders/${id}/`)
      setOrder(data)
    } catch (err) {
      console.error('Error fetching order:', err)
      setError('Failed to load order details')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOrder()
  }, [id])

  const handleOrderUpdated = () => {
    fetchOrder()
    onEditClose()
  }

  const getStatusColor = (status: Order['status']) => {
    switch (status) {
      case 'pending':
        return 'yellow'
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
      case 'standard':
        return 'gray'
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
      <Center h="400px">
        <Spinner size="xl" />
      </Center>
    )
  }

  if (error || !order) {
    return (
      <Box p={6}>
        <Alert status="error">
          <AlertIcon />
          {error || 'Order not found'}
        </Alert>
        <Button
          leftIcon={<ArrowLeft size={16} />}
          mt={4}
          onClick={() => navigate('/orders')}
        >
          Back to Orders
        </Button>
      </Box>
    )
  }

  return (
    <Box p={6}>
      <HStack justify="space-between" mb={6}>
        <HStack spacing={4}>
          <Button
            leftIcon={<ArrowLeft size={16} />}
            variant="ghost"
            onClick={() => navigate('/orders')}
          >
            Back
          </Button>
          <VStack align="start" spacing={0}>
            <Heading size="lg">Order #{order.order_number}</Heading>
            <Text color="gray.600" fontSize="sm">
              Created {new Date(order.created_at).toLocaleDateString()}
            </Text>
          </VStack>
        </HStack>
        <HStack>
          <Badge colorScheme={getStatusColor(order.status)} size="lg" p={2}>
            {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
          </Badge>
          <Button
            leftIcon={<Edit size={16} />}
            colorScheme="blue"
            onClick={onEditOpen}
          >
            Edit Order
          </Button>
        </HStack>
      </HStack>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Customer Information</Heading>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={3}>
              <Box>
                <Text fontWeight="bold">{order.customer_name}</Text>
                {order.customer_company && (
                  <Text color="gray.600">{order.customer_company}</Text>
                )}
              </Box>
              {order.customer_email && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Email
                  </Text>
                  <Text>{order.customer_email}</Text>
                </Box>
              )}
              {order.customer_phone && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Phone
                  </Text>
                  <Text>{order.customer_phone}</Text>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Goods Information</Heading>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={3}>
              <Box>
                <Text fontSize="sm" color="gray.500">
                  Description
                </Text>
                <Text>{order.goods_description}</Text>
              </Box>
              <HStack>
                <Badge colorScheme={getGoodsTypeColor(order.goods_type)}>
                  {order.goods_type.charAt(0).toUpperCase() +
                    order.goods_type.slice(1)}
                </Badge>
              </HStack>
              <SimpleGrid columns={2} spacing={4} width="100%">
                {order.goods_weight && (
                  <Box>
                    <Text fontSize="sm" color="gray.500">
                      Weight
                    </Text>
                    <Text>{order.goods_weight} kg</Text>
                  </Box>
                )}
                {order.goods_volume && (
                  <Box>
                    <Text fontSize="sm" color="gray.500">
                      Volume
                    </Text>
                    <Text>{order.goods_volume} m³</Text>
                  </Box>
                )}
              </SimpleGrid>
              {order.special_instructions && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Special Instructions
                  </Text>
                  <Text>{order.special_instructions}</Text>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md" color="blue.600">
              Pickup Location
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={3}>
              <Box>
                <Text fontWeight="bold">{order.pickup_stop.name}</Text>
                <Text color="gray.600">{order.pickup_stop.address}</Text>
              </Box>
              {order.pickup_stop.contact_name && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Contact
                  </Text>
                  <Text>{order.pickup_stop.contact_name}</Text>
                  {order.pickup_stop.contact_phone && (
                    <Text color="gray.600">
                      {order.pickup_stop.contact_phone}
                    </Text>
                  )}
                </Box>
              )}
              {order.pickup_stop.notes && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Notes
                  </Text>
                  <Text>{order.pickup_stop.notes}</Text>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md" color="green.600">
              Delivery Location
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={3}>
              <Box>
                <Text fontWeight="bold">{order.delivery_stop.name}</Text>
                <Text color="gray.600">{order.delivery_stop.address}</Text>
              </Box>
              {order.delivery_stop.contact_name && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Contact
                  </Text>
                  <Text>{order.delivery_stop.contact_name}</Text>
                  {order.delivery_stop.contact_phone && (
                    <Text color="gray.600">
                      {order.delivery_stop.contact_phone}
                    </Text>
                  )}
                </Box>
              )}
              {order.delivery_stop.notes && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Notes
                  </Text>
                  <Text>{order.delivery_stop.notes}</Text>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>

      {(order.requested_pickup_date || order.requested_delivery_date) && (
        <Card mt={6}>
          <CardHeader>
            <Heading size="md">Requested Dates</Heading>
          </CardHeader>
          <CardBody>
            <HStack spacing={8}>
              {order.requested_pickup_date && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Pickup Date
                  </Text>
                  <Text>
                    {new Date(order.requested_pickup_date).toLocaleDateString()}
                  </Text>
                </Box>
              )}
              {order.requested_delivery_date && (
                <Box>
                  <Text fontSize="sm" color="gray.500">
                    Delivery Date
                  </Text>
                  <Text>
                    {new Date(
                      order.requested_delivery_date
                    ).toLocaleDateString()}
                  </Text>
                </Box>
              )}
            </HStack>
          </CardBody>
        </Card>
      )}

      <OrderForm
        isOpen={isEditOpen}
        onClose={onEditClose}
        onSuccess={handleOrderUpdated}
        order={order}
      />
    </Box>
  )
}
