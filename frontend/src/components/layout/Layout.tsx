import React from 'react'
import { Box, Flex, useColorModeValue } from '@chakra-ui/react'
import { Sidebar } from './Sidebar'

interface LayoutProps {
  children: React.ReactNode
  isFullScreen?: boolean
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  isFullScreen = false,
}) => {
  const bgColor = useColorModeValue('white', 'gray.800')

  return (
    <Flex minH="100vh" w="100vw">
      <Sidebar />

      {/* Main content */}
      <Box flex={1} bg={bgColor} p={isFullScreen ? 0 : 6}>
        {children}
      </Box>
    </Flex>
  )
}
