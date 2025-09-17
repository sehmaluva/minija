import { useEffect, useState } from "react"
import { ProtectedRoute } from "../../components/auth/protected-route"
import {Sidebar}  from "../../components/layout/sidebar"
import { Header } from "../../components/layout/header"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card"
import { Badge } from "../../components/ui/badge"
import { Progress } from "../../components/ui/progress"
import { Building2, Bird, Heart, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react"
import { apiClient } from "../../lib/api"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

interface DashboardStats {
  total_farms: number
  total_flocks: number
  total_birds: number
  healthy_birds: number
  production_rate: number
  feed_consumption: number
  recent_alerts: any[]
  production_trend: any[]
  health_overview: any[]
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiClient.getDashboardStats()
        setStats(data)
      } catch (error) {
        console.error("Failed to fetch dashboard stats:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const mockStats = {
    total_farms: 3,
    total_flocks: 12,
    total_birds: 2450,
    healthy_birds: 2380,
    production_rate: 87.5,
    feed_consumption: 1250,
    recent_alerts: [
      { id: 1, type: "warning", message: "Low feed level in Building A", time: "2 hours ago" },
      { id: 2, type: "info", message: "Vaccination scheduled for Flock B-2", time: "1 day ago" },
    ],
    production_trend: [
      { date: "2024-01-01", eggs: 1200, feed: 800 },
      { date: "2024-01-02", eggs: 1350, feed: 820 },
      { date: "2024-01-03", eggs: 1280, feed: 790 },
      { date: "2024-01-04", eggs: 1420, feed: 850 },
      { date: "2024-01-05", eggs: 1380, feed: 830 },
      { date: "2024-01-06", eggs: 1450, feed: 860 },
      { date: "2024-01-07", eggs: 1520, feed: 880 },
    ],
    health_overview: [
      { status: "Healthy", count: 2380, color: "#15803d" },
      { status: "Under Treatment", count: 45, color: "#d97706" },
      { status: "Quarantined", count: 25, color: "#dc2626" },
    ],
  }

  const displayStats = stats || mockStats
  const healthPercentage = (displayStats.healthy_birds / displayStats.total_birds) * 100

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col lg:pl-72">
          <Header title="Dashboard" subtitle="Overview of your poultry farm operations" />

          <main className="flex-1 overflow-auto p-4 lg:p-8">
            {/* Overview Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Farms</CardTitle>
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{displayStats.total_farms}</div>
                  <p className="text-xs text-muted-foreground">Active farm locations</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Flocks</CardTitle>
                  <Bird className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{displayStats.total_flocks}</div>
                  <p className="text-xs text-muted-foreground">Across all farms</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Birds</CardTitle>
                  <Heart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{displayStats.total_birds.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    {displayStats.healthy_birds.toLocaleString()} healthy ({healthPercentage.toFixed(1)}%)
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Production Rate</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{displayStats.production_rate}%</div>
                  <p className="text-xs text-muted-foreground">Daily average</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 mb-8">
              {/* Production Trend Chart */}
              <Card className="col-span-4">
                <CardHeader>
                  <CardTitle>Production Trend</CardTitle>
                  <CardDescription>Daily egg production and feed consumption over the last 7 days</CardDescription>
                </CardHeader>
                <CardContent className="pl-2">
                  <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={displayStats.production_trend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                      <YAxis />
                      <Tooltip labelFormatter={(value) => new Date(value).toLocaleDateString()} />
                      <Line type="monotone" dataKey="eggs" stroke="var(--color-chart-1)" strokeWidth={2} name="Eggs" />
                      <Line
                        type="monotone"
                        dataKey="feed"
                        stroke="var(--color-chart-2)"
                        strokeWidth={2}
                        name="Feed (kg)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Health Overview */}
              <Card className="col-span-3">
                <CardHeader>
                  <CardTitle>Health Overview</CardTitle>
                  <CardDescription>Current health status of all birds</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {displayStats.health_overview.map((item, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-sm font-medium">{item.status}</span>
                        </div>
                        <div className="text-sm font-bold">{item.count.toLocaleString()}</div>
                      </div>
                    ))}

                    <div className="pt-4">
                      <div className="flex justify-between text-sm mb-2">
                        <span>Overall Health</span>
                        <span>{healthPercentage.toFixed(1)}%</span>
                      </div>
                      <Progress value={healthPercentage} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Alerts */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Alerts</CardTitle>
                <CardDescription>Important notifications and updates from your farms</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {displayStats.recent_alerts.map((alert) => (
                    <div key={alert.id} className="flex items-start gap-3 p-3 rounded-lg border">
                      {alert.type === "warning" ? (
                        <AlertTriangle className="h-5 w-5 text-amber-500 mt-0.5" />
                      ) : (
                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <p className="text-sm font-medium">{alert.message}</p>
                        <p className="text-xs text-muted-foreground">{alert.time}</p>
                      </div>
                      <Badge variant={alert.type === "warning" ? "destructive" : "secondary"}>{alert.type}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
