import React, { useState } from 'react'
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
  SimpleGrid,
} from '@chakra-ui/react'
import { useAuth } from '../../contexts/AuthContext'
import { put } from '../../lib/api'
import type { User, Company } from '../../types/domain'

export const Settings: React.FC = () => {
  const { user, updateUser } = useAuth()

  const [userSettings, setUserSettings] = useState({
    username: user?.username || '',
    email: user?.email || '',
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
  })

  const [companySettings, setCompanySettings] = useState({
    company_name: user?.company_name || '',
    company_email: '',
    company_phone: '',
    company_address: '',
  })

  const [userError, setUserError] = useState('')
  const [companyError, setCompanyError] = useState('')
  const [userSuccess, setUserSuccess] = useState('')
  const [companySuccess, setCompanySuccess] = useState('')
  const [isUserLoading, setIsUserLoading] = useState(false)
  const [isCompanyLoading, setIsCompanyLoading] = useState(false)

  const handleUserChange =
    (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
      setUserSettings((prev) => ({
        ...prev,
        [field]: e.target.value,
      }))
    }

  const handleCompanyChange =
    (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
      setCompanySettings((prev) => ({
        ...prev,
        [field]: e.target.value,
      }))
    }

  const handleUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsUserLoading(true)
    setUserError('')
    setUserSuccess('')

    try {
      const userData: User = await put('/auth/profile/', userSettings)

      // Update user context with new user data
      updateUser(userData)

      setUserSuccess('User settings updated successfully!')
    } catch (err) {
      const error = err as { response?: { data?: { error?: string } } }
      const errorMessage =
        error.response?.data?.error ||
        'Failed to update user settings. Please try again.'
      setUserError(errorMessage)
    } finally {
      setIsUserLoading(false)
    }
  }

  const handleCompanySubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsCompanyLoading(true)
    setCompanyError('')
    setCompanySuccess('')

    try {
      const companyData: Company = await put('/auth/company/', companySettings)

      // Update user context with new company name
      if (user) {
        const updatedUser = {
          ...user,
          company_name: companyData.name,
        }
        updateUser(updatedUser)
      }

      setCompanySuccess('Company settings updated successfully!')
    } catch (err) {
      const error = err as { response?: { data?: { error?: string } } }
      const errorMessage =
        error.response?.data?.error ||
        'Failed to update company settings. Please try again.'
      setCompanyError(errorMessage)
    } finally {
      setIsCompanyLoading(false)
    }
  }

  return (
    <Box maxW="800px" mx="auto" p={4}>
      <Heading size="lg" mb={6}>
        Settings
      </Heading>

      <VStack spacing={8} align="stretch">
        {/* User Settings Section */}
        <Card>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Heading size="md">Personal Information</Heading>
              <Text color="gray.600">Update your personal account details</Text>

              <form onSubmit={handleUserSubmit}>
                <VStack spacing={4}>
                  {userError && (
                    <Alert status="error">
                      <AlertIcon />
                      {userError}
                    </Alert>
                  )}

                  {userSuccess && (
                    <Alert status="success">
                      <AlertIcon />
                      {userSuccess}
                    </Alert>
                  )}

                  <SimpleGrid
                    columns={{ base: 1, md: 2 }}
                    spacing={4}
                    width="100%"
                  >
                    <FormControl>
                      <FormLabel>Username</FormLabel>
                      <Input
                        type="text"
                        value={userSettings.username}
                        onChange={handleUserChange('username')}
                        placeholder="Your username"
                      />
                    </FormControl>

                    <FormControl>
                      <FormLabel>Email</FormLabel>
                      <Input
                        type="email"
                        value={userSettings.email}
                        onChange={handleUserChange('email')}
                        placeholder="your.email@example.com"
                      />
                    </FormControl>

                    <FormControl>
                      <FormLabel>First Name</FormLabel>
                      <Input
                        type="text"
                        value={userSettings.first_name}
                        onChange={handleUserChange('first_name')}
                        placeholder="Your first name"
                      />
                    </FormControl>

                    <FormControl>
                      <FormLabel>Last Name</FormLabel>
                      <Input
                        type="text"
                        value={userSettings.last_name}
                        onChange={handleUserChange('last_name')}
                        placeholder="Your last name"
                      />
                    </FormControl>
                  </SimpleGrid>

                  <Button
                    type="submit"
                    colorScheme="blue"
                    alignSelf="flex-start"
                    isLoading={isUserLoading}
                    loadingText="Saving..."
                  >
                    Save Personal Settings
                  </Button>
                </VStack>
              </form>
            </VStack>
          </CardBody>
        </Card>

        {/* Company Settings Section */}
        <Card>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Heading size="md">Company Information</Heading>
              <Text color="gray.600">Update your company details</Text>

              <form onSubmit={handleCompanySubmit}>
                <VStack spacing={4}>
                  {companyError && (
                    <Alert status="error">
                      <AlertIcon />
                      {companyError}
                    </Alert>
                  )}

                  {companySuccess && (
                    <Alert status="success">
                      <AlertIcon />
                      {companySuccess}
                    </Alert>
                  )}

                  <SimpleGrid
                    columns={{ base: 1, md: 2 }}
                    spacing={4}
                    width="100%"
                  >
                    <FormControl>
                      <FormLabel>Company Name</FormLabel>
                      <Input
                        type="text"
                        value={companySettings.company_name}
                        onChange={handleCompanyChange('company_name')}
                        placeholder="ACME Logistics"
                      />
                    </FormControl>

                    <FormControl>
                      <FormLabel>Company Email</FormLabel>
                      <Input
                        type="email"
                        value={companySettings.company_email}
                        onChange={handleCompanyChange('company_email')}
                        placeholder="contact@company.com"
                      />
                    </FormControl>

                    <FormControl>
                      <FormLabel>Company Phone</FormLabel>
                      <Input
                        type="tel"
                        value={companySettings.company_phone}
                        onChange={handleCompanyChange('company_phone')}
                        placeholder="555-0123"
                      />
                    </FormControl>

                    <FormControl>
                      <FormLabel>Company Address</FormLabel>
                      <Input
                        type="text"
                        value={companySettings.company_address}
                        onChange={handleCompanyChange('company_address')}
                        placeholder="123 Business St, City, State"
                      />
                    </FormControl>
                  </SimpleGrid>

                  <Button
                    type="submit"
                    colorScheme="blue"
                    alignSelf="flex-start"
                    isLoading={isCompanyLoading}
                    loadingText="Saving..."
                  >
                    Save Company Settings
                  </Button>
                </VStack>
              </form>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}
