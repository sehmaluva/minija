import type React from "react"

import { useEffect, useState } from "react"
import { ProtectedRoute } from "../../components/auth/protected-route"
import { Sidebar } from "../../components/layout/sidebar"
import { Header } from "../../components/layout/header"
import { Button } from "../../components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card"
import { Badge } from "../../components/ui/badge"
import { Input } from "../../components/ui/input"
import { Label } from "../../components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs"
import { Progress } from "../../components/ui/progress"
import { Egg, Wheat, TrendingUp, Plus, Target } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts"
import { useToast } from "../../hooks/use-toast"

interface ProductionRecord {
  id: number
  flock_name: string
  date: string
  eggs_collected: number
  feed_consumed: number
  water_consumed: number
  mortality_count: number
  production_rate: number
  feed_conversion_ratio: number
  notes: string
}

interface ProductionSummary {
  total_eggs_today: number
  total_eggs_week: number
  total_eggs_month: number
  average_production_rate: number
  total_feed_consumed: number
  feed_conversion_ratio: number
  mortality_rate: number
  top_performing_flock: string
}

export default function ProductionPage() {
  const [productionRecords, setProductionRecords] = useState<ProductionRecord[]>([])
  const [productionSummary, setProductionSummary] = useState<ProductionSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [formData, setFormData] = useState({
    flock: "",
    date: new Date().toISOString().split("T")[0],
    eggs_collected: "",
    feed_consumed: "",
    water_consumed: "",
    mortality_count: "0",
    notes: "",
  })
  const { toast } = useToast()

  // Mock data for demonstration
  const mockProductionRecords: ProductionRecord[] = [
    {
      id: 1,
      flock_name: "Flock A-1",
      date: "2024-03-15",
      eggs_collected: 742,
      feed_consumed: 85.2,
      water_consumed: 170.4,
      mortality_count: 2,
      production_rate: 87.3,
      feed_conversion_ratio: 2.1,
      notes: "Good production day",
    },
    {
      id: 2,
      flock_name: "Flock C-1",
      date: "2024-03-15",
      eggs_collected: 414,
      feed_consumed: 42.8,
      water_consumed: 85.6,
      mortality_count: 0,
      production_rate: 92.0,
      feed_conversion_ratio: 1.9,
      notes: "Excellent performance",
    },
    {
      id: 3,
      flock_name: "Flock A-1",
      date: "2024-03-14",
      eggs_collected: 728,
      feed_consumed: 84.1,
      water_consumed: 168.2,
      mortality_count: 1,
      production_rate: 85.6,
      feed_conversion_ratio: 2.2,
      notes: "Slight decrease from yesterday",
    },
  ]

  const mockProductionSummary: ProductionSummary = {
    total_eggs_today: 1156,
    total_eggs_week: 8092,
    total_eggs_month: 34567,
    average_production_rate: 89.1,
    total_feed_consumed: 896.5,
    feed_conversion_ratio: 2.0,
    mortality_rate: 0.12,
    top_performing_flock: "Flock C-1",
  }

  // Production trend data for charts
  const productionTrendData = [
    { date: "2024-03-09", eggs: 1089, feed: 128.5, rate: 86.2 },
    { date: "2024-03-10", eggs: 1134, feed: 132.1, rate: 87.8 },
    { date: "2024-03-11", eggs: 1098, feed: 129.7, rate: 85.9 },
    { date: "2024-03-12", eggs: 1167, feed: 135.2, rate: 89.1 },
    { date: "2024-03-13", eggs: 1145, feed: 131.8, rate: 88.3 },
    { date: "2024-03-14", eggs: 1203, feed: 138.9, rate: 91.2 },
    { date: "2024-03-15", eggs: 1156, feed: 128.0, rate: 89.1 },
  ]

  const flockPerformanceData = [
    { name: "Flock A-1", eggs: 742, rate: 87.3, color: "#15803d" },
    { name: "Flock B-2", eggs: 0, rate: 0, color: "#d97706" },
    { name: "Flock C-1", eggs: 414, rate: 92.0, color: "#84cc16" },
  ]

  useEffect(() => {
    const fetchProductionData = async () => {
      try {
        // const records = await apiClient.getProductionRecords();
        // const summary = await apiClient.getProductionSummary();
        setProductionRecords(mockProductionRecords)
        setProductionSummary(mockProductionSummary)
      } catch (error) {
        console.error("Failed to fetch production data:", error)
        setProductionRecords(mockProductionRecords)
        setProductionSummary(mockProductionSummary)
      } finally {
        setLoading(false)
      }
    }

    fetchProductionData()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // await apiClient.createProductionRecord(formData);
      toast({
        title: "Production record added",
        description: "Production data has been recorded successfully.",
      })
      setDialogOpen(false)
      setFormData({
        flock: "",
        date: new Date().toISOString().split("T")[0],
        eggs_collected: "",
        feed_consumed: "",
        water_consumed: "",
        mortality_count: "0",
        notes: "",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to record production data. Please try again.",
        variant: "destructive",
      })
    }
  }

  if (!productionSummary) return null

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col lg:pl-72">
          <Header
            title="Production Management"
            subtitle="Track egg production, feed consumption, and performance metrics"
          />

          <main className="flex-1 overflow-auto p-4 lg:p-8">
            {/* Production Overview Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Today's Eggs</CardTitle>
                  <Egg className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{productionSummary.total_eggs_today.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    {productionSummary.average_production_rate}% production rate
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Weekly Total</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{productionSummary.total_eggs_week.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">+12.5% from last week</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Feed Conversion</CardTitle>
                  <Wheat className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{productionSummary.feed_conversion_ratio}</div>
                  <p className="text-xs text-muted-foreground">kg feed per dozen eggs</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Top Performer</CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{productionSummary.top_performing_flock}</div>
                  <p className="text-xs text-muted-foreground">Best production rate</p>
                </CardContent>
              </Card>
            </div>

            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Production Records</h2>
                <p className="text-muted-foreground">Monitor daily production metrics and performance trends</p>
              </div>

              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Production Record
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Add Production Record</DialogTitle>
                    <DialogDescription>Record daily production data for a specific flock.</DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="flock">Flock</Label>
                        <Select
                          value={formData.flock}
                          onValueChange={(value) => setFormData((prev) => ({ ...prev, flock: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select flock" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">Flock A-1</SelectItem>
                            <SelectItem value="2">Flock B-2</SelectItem>
                            <SelectItem value="3">Flock C-1</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="date">Date</Label>
                        <Input
                          id="date"
                          type="date"
                          value={formData.date}
                          onChange={(e) => setFormData((prev) => ({ ...prev, date: e.target.value }))}
                          required
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="eggs_collected">Eggs Collected</Label>
                        <Input
                          id="eggs_collected"
                          type="number"
                          value={formData.eggs_collected}
                          onChange={(e) => setFormData((prev) => ({ ...prev, eggs_collected: e.target.value }))}
                          placeholder="742"
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="feed_consumed">Feed Consumed (kg)</Label>
                        <Input
                          id="feed_consumed"
                          type="number"
                          step="0.1"
                          value={formData.feed_consumed}
                          onChange={(e) => setFormData((prev) => ({ ...prev, feed_consumed: e.target.value }))}
                          placeholder="85.2"
                          required
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="water_consumed">Water Consumed (L)</Label>
                        <Input
                          id="water_consumed"
                          type="number"
                          step="0.1"
                          value={formData.water_consumed}
                          onChange={(e) => setFormData((prev) => ({ ...prev, water_consumed: e.target.value }))}
                          placeholder="170.4"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="mortality_count">Mortality Count</Label>
                        <Input
                          id="mortality_count"
                          type="number"
                          value={formData.mortality_count}
                          onChange={(e) => setFormData((prev) => ({ ...prev, mortality_count: e.target.value }))}
                          placeholder="0"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="notes">Notes (Optional)</Label>
                      <Input
                        id="notes"
                        value={formData.notes}
                        onChange={(e) => setFormData((prev) => ({ ...prev, notes: e.target.value }))}
                        placeholder="Any observations or notes"
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button type="submit">Record Production</Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <Tabs defaultValue="overview" className="space-y-4">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="trends">Trends</TabsTrigger>
                <TabsTrigger value="records">Records</TabsTrigger>
                <TabsTrigger value="performance">Performance</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Production Trend Chart */}
                  <Card className="col-span-2">
                    <CardHeader>
                      <CardTitle>7-Day Production Trend</CardTitle>
                      <CardDescription>Daily egg production and feed consumption over the last week</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={productionTrendData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                          <YAxis yAxisId="left" />
                          <YAxis yAxisId="right" orientation="right" />
                          <Tooltip labelFormatter={(value) => new Date(value).toLocaleDateString()} />
                          <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="eggs"
                            stroke="var(--color-chart-1)"
                            strokeWidth={2}
                            name="Eggs"
                          />
                          <Line
                            yAxisId="right"
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
                </div>
              </TabsContent>

              <TabsContent value="trends" className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Production Rate Trend */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Production Rate Trend</CardTitle>
                      <CardDescription>Daily production rate percentage</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={productionTrendData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                          <YAxis domain={[80, 95]} />
                          <Tooltip
                            labelFormatter={(value) => new Date(value).toLocaleDateString()}
                            formatter={(value) => [`${value}%`, "Production Rate"]}
                          />
                          <Line type="monotone" dataKey="rate" stroke="var(--color-chart-1)" strokeWidth={2} />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* Flock Performance Comparison */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Flock Performance Today</CardTitle>
                      <CardDescription>Egg production by flock</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={flockPerformanceData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="eggs" fill="var(--color-chart-1)" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="records" className="space-y-4">
                <div className="grid gap-4">
                  {productionRecords.map((record) => (
                    <Card key={record.id}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg">{record.flock_name}</CardTitle>
                            <CardDescription>{new Date(record.date).toLocaleDateString()}</CardDescription>
                          </div>
                          <Badge variant="secondary">{record.production_rate}% rate</Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                          <div>
                            <div className="text-sm font-medium">Eggs Collected</div>
                            <div className="text-2xl font-bold text-primary">
                              {record.eggs_collected.toLocaleString()}
                            </div>
                          </div>
                          <div>
                            <div className="text-sm font-medium">Feed Consumed</div>
                            <div className="text-2xl font-bold">{record.feed_consumed} kg</div>
                          </div>
                          <div>
                            <div className="text-sm font-medium">Water Consumed</div>
                            <div className="text-2xl font-bold">{record.water_consumed} L</div>
                          </div>
                          <div>
                            <div className="text-sm font-medium">FCR</div>
                            <div className="text-2xl font-bold">{record.feed_conversion_ratio}</div>
                          </div>
                          <div>
                            <div className="text-sm font-medium">Mortality</div>
                            <div className="text-2xl font-bold">{record.mortality_count}</div>
                          </div>
                        </div>
                        {record.notes && (
                          <div className="mt-4 pt-4 border-t">
                            <div className="text-sm text-muted-foreground">{record.notes}</div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="performance" className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  {flockPerformanceData.map((flock) => (
                    <Card key={flock.name}>
                      <CardHeader>
                        <CardTitle className="text-lg">{flock.name}</CardTitle>
                        <CardDescription>Performance metrics</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <div className="flex justify-between text-sm mb-2">
                            <span>Production Rate</span>
                            <span>{flock.rate}%</span>
                          </div>
                          <Progress value={flock.rate} className="h-2" />
                        </div>
                        <div>
                          <div className="text-sm font-medium">Today's Eggs</div>
                          <div className="text-2xl font-bold text-primary">{flock.eggs.toLocaleString()}</div>
                        </div>
                        <div className="pt-2 border-t">
                          <div className="text-xs text-muted-foreground">
                            {flock.rate > 90
                              ? "Excellent performance"
                              : flock.rate > 80
                                ? "Good performance"
                                : flock.rate > 0
                                  ? "Below average"
                                  : "Pre-production"}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
