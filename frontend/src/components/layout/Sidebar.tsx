import React from "react";
import { Box, Flex, Heading, Button, Text, Spacer } from "@chakra-ui/react";
import { useAuth } from "../../contexts/AuthContext";

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <Box bg="blue.900" w="250px" flexShrink={0} p={6} shadow="lg">
      <Flex direction="column" h="100%">
        <Heading size="lg" color="white" mb={8}>
          Dashmap
        </Heading>

        <Spacer />

        <Box>
          <Text fontSize="sm" color="blue.200" mb={1}>
            Welcome,
          </Text>
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
              bg: "blue.800",
              borderColor: "blue.400",
            }}
          >
            Logout
          </Button>
        </Box>
      </Flex>
    </Box>
  );
};
