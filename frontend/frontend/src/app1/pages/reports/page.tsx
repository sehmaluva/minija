import { useEffect, useState } from "react"
import { ProtectedRoute } from "../../components/auth/protected-route"
import { Sidebar } from "../../components/layout/sidebar"
import { Header } from "../../components/layout/header"
import { Button } from "../../components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card"
import { Label } from "../../components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs"
import { DatePickerWithRange } from "../../components/ui/date-range-picker"
import { BarChart3, Download, TrendingUp, DollarSign, Percent } from "lucide-react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from "recharts"
import { addDays, format } from "date-fns"
import type { DateRange } from "react-day-picker"
import { useToast } from "../../hooks/use-toast"

interface ReportData {
  financial_summary: {
    total_revenue: number
    total_costs: number
    profit_margin: number
    revenue_growth: number
  }
  production_analytics: {
    total_eggs: number
    average_production_rate: number
    feed_efficiency: number
    mortality_rate: number
  }
  performance_trends: Array<{
    date: string
    production_rate: number
    feed_conversion: number
    mortality: number
    revenue: number
  }>
  flock_comparison: Array<{
    flock_name: string
    production_rate: number
    feed_efficiency: number
    profitability: number
    health_score: number
  }>
  cost_breakdown: Array<{
    category: string
    amount: number
    percentage: number
    color: string
  }>
}

export default function ReportsPage() {
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: addDays(new Date(), -30),
    to: new Date(),
  })
  const [selectedFarm, setSelectedFarm] = useState<string>("all")
  const [reportType, setReportType] = useState<string>("summary")
  const { toast } = useToast()

  // Mock data for demonstration
  const mockReportData: ReportData = {
    financial_summary: {
      total_revenue: 45678.9,
      total_costs: 32145.67,
      profit_margin: 29.6,
      revenue_growth: 12.4,
    },
    production_analytics: {
      total_eggs: 34567,
      average_production_rate: 89.1,
      feed_efficiency: 2.1,
      mortality_rate: 0.12,
    },
    performance_trends: [
      { date: "2024-02-15", production_rate: 85.2, feed_conversion: 2.3, mortality: 0.15, revenue: 1234.56 },
      { date: "2024-02-22", production_rate: 87.1, feed_conversion: 2.2, mortality: 0.13, revenue: 1345.67 },
      { date: "2024-03-01", production_rate: 88.5, feed_conversion: 2.1, mortality: 0.11, revenue: 1456.78 },
      { date: "2024-03-08", production_rate: 89.1, feed_conversion: 2.0, mortality: 0.12, revenue: 1567.89 },
      { date: "2024-03-15", production_rate: 91.2, feed_conversion: 1.9, mortality: 0.1, revenue: 1678.9 },
    ],
    flock_comparison: [
      { flock_name: "Flock A-1", production_rate: 87.3, feed_efficiency: 2.1, profitability: 85.2, health_score: 92 },
      { flock_name: "Flock B-2", production_rate: 0, feed_efficiency: 0, profitability: -15.3, health_score: 78 },
      { flock_name: "Flock C-1", production_rate: 92.0, feed_efficiency: 1.9, profitability: 94.7, health_score: 96 },
    ],
    cost_breakdown: [
      { category: "Feed", amount: 18500.0, percentage: 57.6, color: "#15803d" },
      { category: "Labor", amount: 8200.0, percentage: 25.5, color: "#84cc16" },
      { category: "Healthcare", amount: 2800.0, percentage: 8.7, color: "#d97706" },
      { category: "Utilities", amount: 1645.67, percentage: 5.1, color: "#059669" },
      { category: "Other", amount: 1000.0, percentage: 3.1, color: "#6b7280" },
    ],
  }

  useEffect(() => {
    const fetchReportData = async () => {
      try {
        // const data = await apiClient.getReportData({
        //   start_date: dateRange?.from?.toISOString(),
        //   end_date: dateRange?.to?.toISOString(),
        //   farm: selectedFarm,
        //   report_type: reportType,
        // });
        setReportData(mockReportData)
      } catch (error) {
        console.error("Failed to fetch report data:", error)
        setReportData(mockReportData)
      } finally {
        setLoading(false)
      }
    }

    fetchReportData()
  }, [dateRange, selectedFarm, reportType])

  const handleExportReport = async (format: "pdf" | "excel") => {
    try {
      // await apiClient.exportReport({
      //   format,
      //   start_date: dateRange?.from?.toISOString(),
      //   end_date: dateRange?.to?.toISOString(),
      //   farm: selectedFarm,
      //   report_type: reportType,
      // });
      toast({
        title: "Report exported",
        description: `Report has been exported as ${format.toUpperCase()}.`,
      })
    } catch (error) {
      toast({
        title: "Export failed",
        description: "Failed to export report. Please try again.",
        variant: "destructive",
      })
    }
  }

  if (!reportData) return null

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col lg:pl-72">
          <Header
            title="Analytics & Reports"
            subtitle="Comprehensive insights and performance analytics for your poultry operations"
          />

          <main className="flex-1 overflow-auto p-4 lg:p-8">
            {/* Report Controls */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Report Configuration</CardTitle>
                <CardDescription>Customize your report parameters and date range</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  <div className="space-y-2">
                    <Label>Date Range</Label>
                    <DatePickerWithRange date={dateRange} setDate={setDateRange} />
                  </div>
                  <div className="space-y-2">
                    <Label>Farm</Label>
                    <Select value={selectedFarm} onValueChange={setSelectedFarm}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Farms</SelectItem>
                        <SelectItem value="1">Green Valley Farm</SelectItem>
                        <SelectItem value="2">Sunrise Poultry</SelectItem>
                        <SelectItem value="3">Heritage Farm</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Report Type</Label>
                    <Select value={reportType} onValueChange={setReportType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="summary">Summary Report</SelectItem>
                        <SelectItem value="financial">Financial Report</SelectItem>
                        <SelectItem value="production">Production Report</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Export</Label>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleExportReport("pdf")}>
                        <Download className="h-4 w-4 mr-2" />
                        PDF
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleExportReport("excel")}>
                        <Download className="h-4 w-4 mr-2" />
                        Excel
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Key Metrics Overview */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    ${reportData.financial_summary.total_revenue.toLocaleString()}
                  </div>
                  <p className="text-xs text-muted-foreground flex items-center">
                    <TrendingUp className="h-3 w-3 mr-1 text-green-500" />+{reportData.financial_summary.revenue_growth}
                    % from last period
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Profit Margin</CardTitle>
                  <Percent className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.financial_summary.profit_margin}%</div>
                  <p className="text-xs text-muted-foreground">
                    Profit: $
                    {(
                      reportData.financial_summary.total_revenue - reportData.financial_summary.total_costs
                    ).toLocaleString()}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Production Rate</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.production_analytics.average_production_rate}%</div>
                  <p className="text-xs text-muted-foreground">
                    {reportData.production_analytics.total_eggs.toLocaleString()} eggs total
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Feed Efficiency</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.production_analytics.feed_efficiency}</div>
                  <p className="text-xs text-muted-foreground">kg feed per dozen eggs</p>
                </CardContent>
              </Card>
            </div>

            <Tabs defaultValue="overview" className="space-y-4">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="financial">Financial</TabsTrigger>
                <TabsTrigger value="production">Production</TabsTrigger>
                <TabsTrigger value="comparison">Flock Comparison</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Performance Trends */}
                  <Card className="col-span-2">
                    <CardHeader>
                      <CardTitle>Performance Trends</CardTitle>
                      <CardDescription>Key performance indicators over time</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={350}>
                        <LineChart data={reportData.performance_trends}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" tickFormatter={(value) => format(new Date(value), "MMM dd")} />
                          <YAxis yAxisId="left" />
                          <YAxis yAxisId="right" orientation="right" />
                          <Tooltip labelFormatter={(value) => format(new Date(value), "MMM dd, yyyy")} />
                          <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="production_rate"
                            stroke="var(--color-chart-1)"
                            strokeWidth={2}
                            name="Production Rate (%)"
                          />
                          <Line
                            yAxisId="right"
                            type="monotone"
                            dataKey="feed_conversion"
                            stroke="var(--color-chart-2)"
                            strokeWidth={2}
                            name="Feed Conversion"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="financial" className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Revenue Trend */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Revenue Trend</CardTitle>
                      <CardDescription>Weekly revenue over the selected period</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={reportData.performance_trends}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" tickFormatter={(value) => format(new Date(value), "MMM dd")} />
                          <YAxis />
                          <Tooltip
                            labelFormatter={(value) => format(new Date(value), "MMM dd, yyyy")}
                            formatter={(value) => [`$${value}`, "Revenue"]}
                          />
                          <Area
                            type="monotone"
                            dataKey="revenue"
                            stroke="var(--color-chart-1)"
                            fill="var(--color-chart-1)"
                            fillOpacity={0.3}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* Cost Breakdown */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Cost Breakdown</CardTitle>
                      <CardDescription>Distribution of operational costs</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={reportData.cost_breakdown}
                            cx="50%"
                            cy="50%"
                            outerRadius={80}
                            dataKey="amount"
                            label={({ category, percentage }) => `${category} (${percentage}%)`}
                          >
                            {reportData.cost_breakdown.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value) => [`$${value}`, "Amount"]} />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>

                {/* Cost Details Table */}
                <Card>
                  <CardHeader>
                    <CardTitle>Cost Details</CardTitle>
                    <CardDescription>Detailed breakdown of operational costs</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {reportData.cost_breakdown.map((cost) => (
                        <div key={cost.category} className="flex items-center justify-between p-3 rounded-lg border">
                          <div className="flex items-center gap-3">
                            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: cost.color }} />
                            <div>
                              <div className="font-medium">{cost.category}</div>
                              <div className="text-sm text-muted-foreground">{cost.percentage}% of total</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold">${cost.amount.toLocaleString()}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="production" className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  {/* Production Efficiency */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Production Efficiency</CardTitle>
                      <CardDescription>Feed conversion ratio over time</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={reportData.performance_trends}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" tickFormatter={(value) => format(new Date(value), "MMM dd")} />
                          <YAxis />
                          <Tooltip labelFormatter={(value) => format(new Date(value), "MMM dd, yyyy")} />
                          <Line
                            type="monotone"
                            dataKey="feed_conversion"
                            stroke="var(--color-chart-2)"
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  {/* Mortality Rate */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Mortality Rate</CardTitle>
                      <CardDescription>Weekly mortality percentage</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={reportData.performance_trends}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" tickFormatter={(value) => format(new Date(value), "MMM dd")} />
                          <YAxis />
                          <Tooltip
                            labelFormatter={(value) => format(new Date(value), "MMM dd, yyyy")}
                            formatter={(value) => [`${value}%`, "Mortality Rate"]}
                          />
                          <Bar dataKey="mortality" fill="var(--color-chart-3)" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="comparison" className="space-y-4">
                <div className="grid gap-4">
                  {reportData.flock_comparison.map((flock) => (
                    <Card key={flock.flock_name}>
                      <CardHeader>
                        <CardTitle className="text-lg">{flock.flock_name}</CardTitle>
                        <CardDescription>Performance comparison metrics</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                          <div>
                            <div className="text-sm font-medium mb-2">Production Rate</div>
                            <div className="text-2xl font-bold mb-1">{flock.production_rate}%</div>
                            <div className="w-full bg-secondary rounded-full h-2">
                              <div
                                className="bg-primary h-2 rounded-full"
                                style={{ width: `${flock.production_rate}%` }}
                              />
                            </div>
                          </div>
                          <div>
                            <div className="text-sm font-medium mb-2">Feed Efficiency</div>
                            <div className="text-2xl font-bold mb-1">{flock.feed_efficiency}</div>
                            <div className="text-xs text-muted-foreground">kg/dozen eggs</div>
                          </div>
                          <div>
                            <div className="text-sm font-medium mb-2">Profitability</div>
                            <div
                              className={`text-2xl font-bold mb-1 ${flock.profitability > 0 ? "text-green-600" : "text-red-600"}`}
                            >
                              {flock.profitability > 0 ? "+" : ""}
                              {flock.profitability}%
                            </div>
                            <div className="text-xs text-muted-foreground">vs. average</div>
                          </div>
                          <div>
                            <div className="text-sm font-medium mb-2">Health Score</div>
                            <div className="text-2xl font-bold mb-1">{flock.health_score}/100</div>
                            <div className="w-full bg-secondary rounded-full h-2">
                              <div
                                className="bg-green-500 h-2 rounded-full"
                                style={{ width: `${flock.health_score}%` }}
                              />
                            </div>
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
