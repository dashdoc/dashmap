import React, { useState } from 'react'
import { Box } from '@chakra-ui/react'
import { LoginForm } from './LoginForm'
import { SignupForm } from './SignupForm'

export const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true)

  return (
    <Box
      minH="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      w="100vw"
      bgGradient="linear(to-bl, blue.200, purple.200)"
    >
      {isLogin ? (
        <LoginForm onSwitchToSignup={() => setIsLogin(false)} />
      ) : (
        <SignupForm onSwitchToLogin={() => setIsLogin(true)} />
      )}
    </Box>
  )
}
