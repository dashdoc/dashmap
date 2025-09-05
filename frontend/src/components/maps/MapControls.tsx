import React from 'react'
import { Box, Text, VStack, HStack, Switch, FormLabel } from '@chakra-ui/react'
import type { MapControls } from '../../types/map'

interface MapControlsProps {
  controls: MapControls
  onControlChange: (control: keyof MapControls, value: boolean) => void
}

const MapControlsComponent: React.FC<MapControlsProps> = ({
  controls,
  onControlChange,
}) => {
  return (
    <Box
      position="absolute"
      top="20px"
      left="20px"
      bg="white"
      borderRadius="lg"
      boxShadow="lg"
      p={4}
      minW="200px"
      zIndex={1000}
    >
      <Text fontSize="md" fontWeight="bold" mb={3}>
        Map Controls
      </Text>
      <VStack spacing={3} align="stretch">
        <HStack justify="space-between">
          <FormLabel htmlFor="orders-toggle" mb={0} fontSize="sm">
            Orders
          </FormLabel>
          <Switch
            id="orders-toggle"
            isChecked={controls.showOrders}
            onChange={(e) => onControlChange('showOrders', e.target.checked)}
            colorScheme="blue"
          />
        </HStack>
        <HStack justify="space-between">
          <FormLabel htmlFor="vehicles-toggle" mb={0} fontSize="sm">
            Vehicles
          </FormLabel>
          <Switch
            id="vehicles-toggle"
            isChecked={controls.showVehicles}
            onChange={(e) => onControlChange('showVehicles', e.target.checked)}
            colorScheme="blue"
          />
        </HStack>
        <HStack justify="space-between">
          <FormLabel htmlFor="trips-toggle" mb={0} fontSize="sm">
            Trips
          </FormLabel>
          <Switch
            id="trips-toggle"
            isChecked={controls.showTrips}
            onChange={(e) => onControlChange('showTrips', e.target.checked)}
            colorScheme="blue"
          />
        </HStack>
      </VStack>
    </Box>
  )
}

export default MapControlsComponent
