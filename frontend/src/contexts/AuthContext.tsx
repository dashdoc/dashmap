import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from 'react'
import type { User } from '../types/domain'
import { get, post } from '../lib/api'
import axios from 'axios'

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  signup: (userData: SignupData) => Promise<void>
  updateUser: (userData: User) => void
  loading: boolean
}

interface SignupData {
  username: string
  password: string
  email: string
  first_name: string
  last_name: string
  company_name: string
  company_address: string
  company_phone: string
  company_email: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('token')
  )
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('token')
      const storedUser = localStorage.getItem('user')

      if (storedToken) {
        setToken(storedToken)
        axios.defaults.headers.common['Authorization'] = `Token ${storedToken}`

        // First set the user from localStorage as fallback
        if (storedUser) {
          setUser(JSON.parse(storedUser))
        }

        // Then try to refresh user data from server
        try {
          const userData = await get<User>('/auth/profile/')
          const profileData: User = userData
          setUser(profileData)
          localStorage.setItem('user', JSON.stringify(profileData))
        } catch (error) {
          const err = error as { response?: { status?: number } }
          console.error('Failed to fetch user profile:', error)

          // Only clear auth if the token is invalid (401/403)
          if (err.response?.status === 401 || err.response?.status === 403) {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            delete axios.defaults.headers.common['Authorization']
            setToken(null)
            setUser(null)
          }
          // For other errors (network issues, server down, etc.), keep the user logged in with cached data
        }
      }
      setLoading(false)
    }

    initializeAuth()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const loginData: {
        token: string
        user_id: number
        username: string
        email: string
        first_name: string
        last_name: string
        company_id: number
        company_name: string
      } = await post('/auth/login/', {
        username,
        password,
      })

      const {
        token: newToken,
        user_id,
        username: resUsername,
        email,
        first_name,
        last_name,
        company_id,
        company_name,
      } = loginData

      const userData: User = {
        id: user_id,
        username: resUsername,
        email,
        first_name,
        last_name,
        company_id,
        company_name,
      }

      setToken(newToken)
      setUser(userData)

      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      if (token) {
        await post('/auth/logout/', {})
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setToken(null)
      setUser(null)
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }

  const signup = async (userData: SignupData) => {
    try {
      await post('/auth/register/', {
        username: userData.username,
        password: userData.password,
        email: userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
        company_name: userData.company_name,
        company_address: userData.company_address,
        company_phone: userData.company_phone,
        company_email: userData.company_email,
      })

      await login(userData.username, userData.password)
    } catch (error) {
      console.error('Signup failed:', error)
      throw error
    }
  }

  const updateUser = (userData: User) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    signup,
    updateUser,
    loading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
