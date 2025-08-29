import React from 'react';
import {
  Box,
  Flex,
  Heading,
  Button,
  Text,
  HStack,
  Spacer,
  useColorModeValue,
} from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const handleLogout = async () => {
    await logout();
  };

  return (
    <Box minH="100vh">
      <Box
        bg={bgColor}
        borderBottom="1px"
        borderColor={borderColor}
        px={6}
        py={4}
        shadow="sm"
      >
        <Flex align="center">
          <Heading size="lg" color="blue.500">
            DashMap
          </Heading>
          <Spacer />
          <HStack spacing={4}>
            <Text fontSize="sm" color="gray.600">
              Welcome, {user?.first_name} {user?.last_name}
            </Text>
            <Text fontSize="sm" color="gray.500">
              {user?.company_name}
            </Text>
            <Button size="sm" variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          </HStack>
        </Flex>
      </Box>
      
      <Box p={6}>
        {children}
      </Box>
    </Box>
  );
};