import React from 'react'
import {
  Box,
  Flex,
  Heading,
  Button,
  Text,
  Spacer,
  VStack,
} from '@chakra-ui/react'
import { Map, Route, Truck, Package, Settings } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
  }

  const tabs = [
    { name: 'Map', path: '/map', icon: Map },
    { name: 'Orders', path: '/orders', icon: Package },
    { name: 'Trips', path: '/trips', icon: Route },
    { name: 'Vehicles', path: '/vehicles', icon: Truck },
    { name: 'Settings', path: '/settings', icon: Settings },
  ]

  return (
    <Box w="250px" flexShrink={0} p={6} shadow="lg" bg="blue.900">
      <Flex direction="column" h="100%">
        <Heading size="lg" color="white" mb={8}>
          Dashmap
        </Heading>

        <VStack spacing={2} align="stretch" mb={8}>
          {tabs.map((tab) => {
            const isActive = location.pathname === tab.path
            const IconComponent = tab.icon
            return (
              <Button
                key={tab.name}
                variant={isActive ? 'solid' : 'ghost'}
                colorScheme={isActive ? 'blue' : undefined}
                color={isActive ? 'white' : 'blue.200'}
                bg={isActive ? 'blue.700' : 'transparent'}
                justifyContent="flex-start"
                leftIcon={<IconComponent size={18} />}
                onClick={() => navigate(tab.path)}
                _hover={{
                  bg: isActive ? 'blue.600' : 'blue.800',
                  color: 'white',
                }}
              >
                {tab.name}
              </Button>
            )
          })}
        </VStack>

        <Spacer />

        <Box>
          <Text fontSize="md" color="white" fontWeight="semibold" mb={1}>
            {user?.first_name} {user?.last_name}
          </Text>
          <Text fontSize="sm" color="blue.300" mb={4}>
            {user?.company_name}
          </Text>
          <Button
            size="sm"
            colorScheme="blue"
            variant="outline"
            onClick={handleLogout}
            color="white"
            borderColor="blue.500"
            _hover={{
              bg: 'blue.800',
              borderColor: 'blue.400',
            }}
          >
            Logout
          </Button>
        </Box>
      </Flex>
    </Box>
  )
}
