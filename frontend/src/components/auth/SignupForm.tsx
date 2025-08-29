import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Text,
  Alert,
  AlertIcon,
  Heading,
  Card,
  CardBody,
  Link,
  SimpleGrid,
  Divider,
} from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';

interface SignupFormProps {
  onSwitchToLogin: () => void;
}

export const SignupForm: React.FC<SignupFormProps> = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    first_name: '',
    last_name: '',
    company_name: '',
    company_address: '',
    company_phone: '',
    company_email: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { signup } = useAuth();

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await signup(formData);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box maxW="600px" mx="auto" mt={8}>
      <Card>
        <CardBody>
          <VStack spacing={6}>
            <Heading size="lg" textAlign="center">
              Create Account
            </Heading>
            <Text color="gray.600" textAlign="center">
              Sign up to start managing your vehicle routes
            </Text>
            
            <form onSubmit={handleSubmit} style={{ width: '100%' }}>
              <VStack spacing={4}>
                {error && (
                  <Alert status="error">
                    <AlertIcon />
                    {error}
                  </Alert>
                )}
                
                <Text fontWeight="semibold" alignSelf="start">Personal Information</Text>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} width="100%">
                  <FormControl isRequired>
                    <FormLabel>Username</FormLabel>
                    <Input
                      type="text"
                      value={formData.username}
                      onChange={handleChange('username')}
                      placeholder="Choose a username"
                    />
                  </FormControl>
                  
                  <FormControl isRequired>
                    <FormLabel>Password</FormLabel>
                    <Input
                      type="password"
                      value={formData.password}
                      onChange={handleChange('password')}
                      placeholder="Create a password"
                    />
                  </FormControl>
                  
                  <FormControl isRequired>
                    <FormLabel>First Name</FormLabel>
                    <Input
                      type="text"
                      value={formData.first_name}
                      onChange={handleChange('first_name')}
                      placeholder="Your first name"
                    />
                  </FormControl>
                  
                  <FormControl isRequired>
                    <FormLabel>Last Name</FormLabel>
                    <Input
                      type="text"
                      value={formData.last_name}
                      onChange={handleChange('last_name')}
                      placeholder="Your last name"
                    />
                  </FormControl>
                  
                  <FormControl isRequired>
                    <FormLabel>Email</FormLabel>
                    <Input
                      type="email"
                      value={formData.email}
                      onChange={handleChange('email')}
                      placeholder="your.email@example.com"
                    />
                  </FormControl>
                </SimpleGrid>
                
                <Divider />
                
                <Text fontWeight="semibold" alignSelf="start">Company Information</Text>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} width="100%">
                  <FormControl isRequired>
                    <FormLabel>Company Name</FormLabel>
                    <Input
                      type="text"
                      value={formData.company_name}
                      onChange={handleChange('company_name')}
                      placeholder="ACME Logistics"
                    />
                  </FormControl>
                  
                  <FormControl isRequired>
                    <FormLabel>Company Email</FormLabel>
                    <Input
                      type="email"
                      value={formData.company_email}
                      onChange={handleChange('company_email')}
                      placeholder="contact@company.com"
                    />
                  </FormControl>
                  
                  <FormControl isRequired>
                    <FormLabel>Company Phone</FormLabel>
                    <Input
                      type="tel"
                      value={formData.company_phone}
                      onChange={handleChange('company_phone')}
                      placeholder="555-0123"
                    />
                  </FormControl>
                  
                  <FormControl isRequired>
                    <FormLabel>Company Address</FormLabel>
                    <Input
                      type="text"
                      value={formData.company_address}
                      onChange={handleChange('company_address')}
                      placeholder="123 Business St, City, State"
                    />
                  </FormControl>
                </SimpleGrid>
                
                <Button
                  type="submit"
                  colorScheme="blue"
                  width="100%"
                  isLoading={isLoading}
                  loadingText="Creating account..."
                >
                  Create Account
                </Button>
              </VStack>
            </form>
            
            <Text fontSize="sm" textAlign="center">
              Already have an account?{' '}
              <Link color="blue.500" onClick={onSwitchToLogin} cursor="pointer">
                Sign in here
              </Link>
            </Text>
          </VStack>
        </CardBody>
      </Card>
    </Box>
  );
};