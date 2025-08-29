import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  company_id: number;
  company_name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (userData: SignupData) => Promise<void>;
  loading: boolean;
}

interface SignupData {
  username: string;
  password: string;
  email: string;
  first_name: string;
  last_name: string;
  company_name: string;
  company_address: string;
  company_phone: string;
  company_email: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE_URL = 'http://localhost:8000/api';

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      axios.defaults.headers.common['Authorization'] = `Token ${storedToken}`;
    }
    setLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login/`, {
        username,
        password
      }, {
        headers: {}
      });

      const { token: newToken, user_id, username: resUsername, email, first_name, last_name, company_id, company_name } = response.data;
      
      const userData: User = {
        id: user_id,
        username: resUsername,
        email,
        first_name,
        last_name,
        company_id,
        company_name
      };

      setToken(newToken);
      setUser(userData);
      
      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(userData));
      
      axios.defaults.headers.common['Authorization'] = `Token ${newToken}`;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(`${API_BASE_URL}/auth/logout/`, {}, {
          headers: { Authorization: `Token ${token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setToken(null);
      setUser(null);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const signup = async (userData: SignupData) => {
    try {
      await axios.post(`${API_BASE_URL}/auth/register/`, {
        username: userData.username,
        password: userData.password,
        email: userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
        company_name: userData.company_name,
        company_address: userData.company_address,
        company_phone: userData.company_phone,
        company_email: userData.company_email
      }, {
        headers: {}
      });

      await login(userData.username, userData.password);
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    signup,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};