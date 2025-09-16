"use client"

import type React from "react"
import { createContext, useContext, useEffect, useState } from "react"
import { apiClient } from "../lib/api"

interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: string
  farm?: any
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (userData: any) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("auth_token")
    if (token) {
      apiClient.setToken(token)
      // You might want to validate the token here
      // For now, we'll assume it's valid
    }
    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.login(email, password)
      apiClient.setToken(response.access)
      setUser(response.user)
      localStorage.setItem("refresh_token", response.refresh)
    } catch (error) {
      throw error
    }
  }

  const register = async (userData: any) => {
    try {
      const response = await apiClient.register(userData)
      apiClient.setToken(response.access)
      setUser(response.user)
      localStorage.setItem("refresh_token", response.refresh)
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    apiClient.clearToken()
    setUser(null)
    localStorage.removeItem("refresh_token")
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
