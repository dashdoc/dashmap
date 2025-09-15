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
    <Flex h="100vh" w="100vw" overflow="hidden">
      <Sidebar />

      {/* Main content needs its own scroll container so the sidebar stays fixed */}
      <Box
        flex={1}
        h="100%"
        bg={bgColor}
        p={isFullScreen ? 0 : 6}
        overflowY="auto"
      >
        {children}
      </Box>
    </Flex>
  )
}
