"use client"

export const dynamic = 'force-dynamic'

import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Bird, Heart, Wheat, TrendingUp, AlertTriangle, Calendar, DollarSign } from "lucide-react"
import { useEffect, useState } from "react"
import { dashboardAPI } from "@/lib/api-functions"

interface DashboardData {
  farm_statistics: {
    total_farms: number
    total_capacity: number
    occupied_capacity: number
  }
  flock_statistics: {
    total_flocks: number
    total_birds: number
    healthy_birds: number
    mortality_rate: number
  }
  production_analytics: {
    egg_production: {
      total_eggs_today: number
      average_production_rate: number
    }
    feed_consumption: {
      total_feed_today: number
    }
  }
  financial_analytics: {
    total_revenue: number
  }
  recent_alerts: Array<{
    id: number
    alert_type: string
    message: string
    created_at: string
    is_resolved: boolean
  }>
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await dashboardAPI.getAnalytics() as DashboardData
        setData(response)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 text-destructive mx-auto mb-4" />
            <p className="text-destructive">{error}</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (!data) return null

  const stats = {
    totalBirds: data.flock_statistics.total_birds,
    healthyBirds: data.flock_statistics.healthy_birds,
    dailyEggs: data.production_analytics.egg_production.total_eggs_today,
    feedConsumption: data.production_analytics.feed_consumption.total_feed_today,
    mortalityRate: data.flock_statistics.mortality_rate,
    revenue: data.financial_analytics.total_revenue,
  }

  const recentAlerts = data.recent_alerts.slice(0, 3).map(alert => ({
    id: alert.id,
    type: alert.alert_type.toLowerCase(),
    message: alert.message,
    time: new Date(alert.created_at).toLocaleDateString(),
  }))

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-balance">Dashboard</h1>
          <p className="text-muted-foreground text-pretty">Welcome back! Here's what's happening on your farm today.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Birds</CardTitle>
              <Bird className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalBirds.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600">+2.5%</span> from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Healthy Birds</CardTitle>
              <Heart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.healthyBirds.toLocaleString()}</div>
              <div className="mt-2">
                <Progress value={(stats.healthyBirds / stats.totalBirds) * 100} className="h-2" />
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {((stats.healthyBirds / stats.totalBirds) * 100).toFixed(1)}% healthy
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Daily Eggs</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.dailyEggs.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600">+5.2%</span> from yesterday
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.revenue.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">This month</p>
            </CardContent>
          </Card>
        </div>

        {/* Content Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Recent Alerts */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Recent Alerts
              </CardTitle>
              <CardDescription>Important notifications requiring your attention</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentAlerts.map((alert) => (
                <div key={alert.id} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                  <div className="flex-1">
                    <p className="text-sm font-medium">{alert.message}</p>
                    <p className="text-xs text-muted-foreground mt-1">{alert.time}</p>
                  </div>
                  <Badge variant={alert.type === "health" ? "destructive" : "secondary"}>{alert.type}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Farm Overview</CardTitle>
              <CardDescription>Key metrics at a glance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Wheat className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Feed Consumption</span>
                </div>
                <span className="font-medium">{stats.feedConsumption} kg/day</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Heart className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Mortality Rate</span>
                </div>
                <span className="font-medium">{stats.mortalityRate}%</span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Next Vaccination</span>
                </div>
                <span className="font-medium">3 days</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
