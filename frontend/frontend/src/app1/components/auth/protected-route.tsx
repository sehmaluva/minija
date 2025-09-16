"use client"

import type React from "react"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "../../contexts/auth-context"
import { Card, CardContent } from "../../components/ui/card"
import { Bird } from "lucide-react"

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/login")
    }
  }, [isAuthenticated, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="w-96">
          <CardContent className="flex flex-col items-center justify-center p-8">
            <Bird className="h-12 w-12 text-primary animate-pulse mb-4" />
            <h1 className="text-2xl font-semibold text-center mb-2">PoultryPro</h1>
            <p className="text-muted-foreground text-center">Loading...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
