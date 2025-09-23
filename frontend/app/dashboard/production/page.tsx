"use client"

import { useState } from "react"

export const dynamic = 'force-dynamic'

import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts"
import { TrendingUp, Egg, DollarSign, Wheat, Download } from "lucide-react"

export default function ProductionPage() {
  const [activeTab, setActiveTab] = useState("overview")
  const [timeRange, setTimeRange] = useState("7d")

  // Mock data - replace with actual API calls
  const productionStats = {
    dailyEggs: 1850,
    weeklyEggs: 12950,
    monthlyEggs: 55420,
    eggProductionRate: 75.5,
    feedConsumption: 125,
    feedEfficiency: 2.1,
    revenue: 15420,
    profit: 8950,
  }

  const eggProductionData = [
    { date: "2024-01-09", eggs: 1720, target: 1800 },
    { date: "2024-01-10", eggs: 1780, target: 1800 },
    { date: "2024-01-11", eggs: 1850, target: 1800 },
    { date: "2024-01-12", eggs: 1920, target: 1800 },
    { date: "2024-01-13", eggs: 1680, target: 1800 },
    { date: "2024-01-14", eggs: 1750, target: 1800 },
    { date: "2024-01-15", eggs: 1850, target: 1800 },
  ]

  const feedConsumptionData = [
    { date: "2024-01-09", consumption: 120, cost: 240 },
    { date: "2024-01-10", consumption: 125, cost: 250 },
    { date: "2024-01-11", consumption: 130, cost: 260 },
    { date: "2024-01-12", consumption: 128, cost: 256 },
    { date: "2024-01-13", consumption: 122, cost: 244 },
    { date: "2024-01-14", consumption: 127, cost: 254 },
    { date: "2024-01-15", consumption: 125, cost: 250 },
  ]

  const batchPerformance = [
    { batch: "B001", eggs: 450, rate: 90, efficiency: 2.0 },
    { batch: "B002", eggs: 680, rate: 85, efficiency: 2.2 },
    { batch: "B003", eggs: 720, rate: 78, efficiency: 2.4 },
  ]

  const revenueData = [
    { name: "Eggs", value: 12500, color: "#15803d" },
    { name: "Meat", value: 2920, color: "#84cc16" },
    { name: "Other", value: 0, color: "#6b7280" },
  ]

  const getPerformanceColor = (rate: number) => {
    if (rate >= 85) return "text-green-600"
    if (rate >= 70) return "text-yellow-600"
    return "text-red-600"
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-balance">Production Analytics</h1>
            <p className="text-muted-foreground text-pretty">
              Track egg production, feed consumption, and financial performance
            </p>
          </div>
          <div className="flex gap-2">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
                <SelectItem value="1y">Last year</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="eggs">Egg Production</TabsTrigger>
            <TabsTrigger value="feed">Feed Analysis</TabsTrigger>
            <TabsTrigger value="financial">Financial</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Daily Eggs</CardTitle>
                  <Egg className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{productionStats.dailyEggs.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <TrendingUp className="h-3 w-3 text-green-600" />
                    <span className="text-green-600">+5.2%</span> from yesterday
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Production Rate</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{productionStats.eggProductionRate}%</div>
                  <div className="mt-2">
                    <Progress value={productionStats.eggProductionRate} className="h-2" />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Target: 80%</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Feed Efficiency</CardTitle>
                  <Wheat className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{productionStats.feedEfficiency}</div>
                  <p className="text-xs text-muted-foreground">kg feed per dozen eggs</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatCurrency(productionStats.revenue)}</div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <TrendingUp className="h-3 w-3 text-green-600" />
                    <span className="text-green-600">+12.5%</span> from last month
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Charts Grid */}
            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Egg Production Trend</CardTitle>
                  <CardDescription>Daily egg production vs target</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={eggProductionData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
                      <YAxis />
                      <Tooltip labelFormatter={(date) => new Date(date).toLocaleDateString()} />
                      <Line type="monotone" dataKey="eggs" stroke="#15803d" strokeWidth={2} />
                      <Line type="monotone" dataKey="target" stroke="#84cc16" strokeDasharray="5 5" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Batch Performance</CardTitle>
                  <CardDescription>Production rate by batch</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {batchPerformance.map((batch) => (
                      <div key={batch.batch} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{batch.batch}</p>
                          <p className="text-sm text-muted-foreground">{batch.eggs} eggs today</p>
                        </div>
                        <div className="text-right">
                          <p className={`font-medium ${getPerformanceColor(batch.rate)}`}>{batch.rate}%</p>
                          <p className="text-sm text-muted-foreground">{batch.efficiency} kg/dozen</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Egg Production Tab */}
          <TabsContent value="eggs" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Today</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{productionStats.dailyEggs.toLocaleString()}</div>
                  <p className="text-sm text-muted-foreground">eggs collected</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">This Week</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{productionStats.weeklyEggs.toLocaleString()}</div>
                  <p className="text-sm text-muted-foreground">eggs collected</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">This Month</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{productionStats.monthlyEggs.toLocaleString()}</div>
                  <p className="text-sm text-muted-foreground">eggs collected</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Production Trends</CardTitle>
                <CardDescription>Detailed egg production analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={eggProductionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
                    <YAxis />
                    <Tooltip labelFormatter={(date) => new Date(date).toLocaleDateString()} />
                    <Line type="monotone" dataKey="eggs" stroke="#15803d" strokeWidth={3} />
                    <Line type="monotone" dataKey="target" stroke="#84cc16" strokeDasharray="5 5" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Feed Analysis Tab */}
          <TabsContent value="feed" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Daily Consumption</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{productionStats.feedConsumption} kg</div>
                  <p className="text-xs text-muted-foreground">feed consumed today</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Feed Efficiency</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{productionStats.feedEfficiency}</div>
                  <p className="text-xs text-muted-foreground">kg per dozen eggs</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Daily Cost</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">$250</div>
                  <p className="text-xs text-muted-foreground">feed cost today</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Cost per Egg</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">$0.135</div>
                  <p className="text-xs text-muted-foreground">feed cost per egg</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Feed Consumption & Cost</CardTitle>
                <CardDescription>Daily feed usage and associated costs</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={feedConsumptionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip labelFormatter={(date) => new Date(date).toLocaleDateString()} />
                    <Bar yAxisId="left" dataKey="consumption" fill="#15803d" name="Consumption (kg)" />
                    <Bar yAxisId="right" dataKey="cost" fill="#84cc16" name="Cost ($)" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Financial Tab */}
          <TabsContent value="financial" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{formatCurrency(productionStats.revenue)}</div>
                  <p className="text-xs text-muted-foreground">total income</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Monthly Profit</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{formatCurrency(productionStats.profit)}</div>
                  <p className="text-xs text-muted-foreground">net profit</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Profit Margin</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {((productionStats.profit / productionStats.revenue) * 100).toFixed(1)}%
                  </div>
                  <p className="text-xs text-muted-foreground">profit margin</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Revenue per Bird</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">$6.29</div>
                  <p className="text-xs text-muted-foreground">monthly average</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Revenue Breakdown</CardTitle>
                  <CardDescription>Income sources this month</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={revenueData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${formatCurrency(value)}`}
                      >
                        {revenueData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(value as number)} />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Financial Summary</CardTitle>
                  <CardDescription>Key financial metrics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm">Gross Revenue</span>
                    <span className="font-medium">{formatCurrency(productionStats.revenue)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Feed Costs</span>
                    <span className="font-medium">$4,200</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Labor Costs</span>
                    <span className="font-medium">$1,800</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Other Expenses</span>
                    <span className="font-medium">$470</span>
                  </div>
                  <hr />
                  <div className="flex justify-between font-medium">
                    <span>Net Profit</span>
                    <span className="text-green-600">{formatCurrency(productionStats.profit)}</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
