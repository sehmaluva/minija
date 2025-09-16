"use client"

import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Bird, Heart, Wheat, TrendingUp, AlertTriangle, Calendar, DollarSign } from "lucide-react"

export default function DashboardPage() {
  // Mock data - replace with actual API calls
  const stats = {
    totalBirds: 2450,
    healthyBirds: 2380,
    dailyEggs: 1850,
    feedConsumption: 125,
    mortalityRate: 2.8,
    revenue: 15420,
  }

  const recentAlerts = [
    { id: 1, type: "health", message: "Vaccination due for Coop A", time: "2 hours ago" },
    { id: 2, type: "feed", message: "Low feed stock in Barn 3", time: "4 hours ago" },
    { id: 3, type: "production", message: "Egg production below average", time: "1 day ago" },
  ]

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
