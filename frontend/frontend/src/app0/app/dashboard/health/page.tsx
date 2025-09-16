"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Textarea } from "@/components/ui/textarea"
import { Progress } from "@/components/ui/progress"
import { Heart, Plus, Calendar, AlertTriangle, Syringe, FileText, TrendingUp, Activity } from "lucide-react"

export default function HealthPage() {
  const [activeTab, setActiveTab] = useState("overview")

  // Mock data - replace with actual API calls
  const healthStats = {
    totalBirds: 2450,
    healthyBirds: 2380,
    sickBirds: 45,
    quarantineBirds: 25,
    mortalityRate: 2.8,
    vaccinationRate: 95.2,
  }

  const vaccinations = [
    {
      id: 1,
      vaccine: "Newcastle Disease",
      batch: "B001",
      dueDate: "2024-01-20",
      status: "due",
      birdsCount: 500,
    },
    {
      id: 2,
      vaccine: "Infectious Bronchitis",
      batch: "B002",
      dueDate: "2024-01-18",
      status: "overdue",
      birdsCount: 750,
    },
    {
      id: 3,
      vaccine: "Fowl Pox",
      batch: "B003",
      dueDate: "2024-01-25",
      status: "scheduled",
      birdsCount: 300,
    },
  ]

  const healthRecords = [
    {
      id: 1,
      date: "2024-01-15",
      batch: "B001",
      issue: "Respiratory symptoms",
      treatment: "Antibiotics administered",
      status: "recovered",
      veterinarian: "Dr. Sarah Johnson",
    },
    {
      id: 2,
      date: "2024-01-14",
      batch: "B002",
      issue: "Digestive issues",
      treatment: "Dietary adjustment",
      status: "monitoring",
      veterinarian: "Dr. Sarah Johnson",
    },
    {
      id: 3,
      date: "2024-01-12",
      batch: "B003",
      issue: "Routine checkup",
      treatment: "Preventive care",
      status: "healthy",
      veterinarian: "Dr. Mike Wilson",
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
      case "recovered":
      case "completed":
        return "bg-green-100 text-green-800"
      case "monitoring":
      case "due":
      case "scheduled":
        return "bg-yellow-100 text-yellow-800"
      case "sick":
      case "overdue":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const AddVaccinationDialog = () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Schedule Vaccination
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Schedule Vaccination</DialogTitle>
          <DialogDescription>Schedule a vaccination for a batch of birds</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="vaccine">Vaccine Type</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select vaccine" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newcastle">Newcastle Disease</SelectItem>
                <SelectItem value="bronchitis">Infectious Bronchitis</SelectItem>
                <SelectItem value="fowlpox">Fowl Pox</SelectItem>
                <SelectItem value="marek">Marek's Disease</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="batch">Batch</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select batch" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="b001">Batch B001 - Rhode Island Red</SelectItem>
                <SelectItem value="b002">Batch B002 - Leghorn</SelectItem>
                <SelectItem value="b003">Batch B003 - Sussex</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="date">Vaccination Date</Label>
            <Input id="date" type="date" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="veterinarian">Veterinarian</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select veterinarian" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sarah">Dr. Sarah Johnson</SelectItem>
                <SelectItem value="mike">Dr. Mike Wilson</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button className="w-full">Schedule Vaccination</Button>
        </div>
      </DialogContent>
    </Dialog>
  )

  const AddHealthRecordDialog = () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Health Record
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Health Record</DialogTitle>
          <DialogDescription>Record a health issue or treatment</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="batch">Batch/Bird ID</Label>
            <Input id="batch" placeholder="e.g., B001 or B001-001" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="issue">Health Issue</Label>
            <Input id="issue" placeholder="Describe the health issue" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="treatment">Treatment</Label>
            <Textarea id="treatment" placeholder="Describe the treatment given" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="veterinarian">Veterinarian</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select veterinarian" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sarah">Dr. Sarah Johnson</SelectItem>
                <SelectItem value="mike">Dr. Mike Wilson</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="status">Status</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="monitoring">Monitoring</SelectItem>
                <SelectItem value="treating">Under Treatment</SelectItem>
                <SelectItem value="recovered">Recovered</SelectItem>
                <SelectItem value="quarantine">Quarantine</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button className="w-full">Add Record</Button>
        </div>
      </DialogContent>
    </Dialog>
  )

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-balance">Health Monitoring</h1>
          <p className="text-muted-foreground text-pretty">Track bird health, vaccinations, and veterinary records</p>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="vaccinations">Vaccinations</TabsTrigger>
            <TabsTrigger value="records">Health Records</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Healthy Birds</CardTitle>
                  <Heart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{healthStats.healthyBirds.toLocaleString()}</div>
                  <div className="mt-2">
                    <Progress value={(healthStats.healthyBirds / healthStats.totalBirds) * 100} className="h-2" />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {((healthStats.healthyBirds / healthStats.totalBirds) * 100).toFixed(1)}% of total
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Sick Birds</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{healthStats.sickBirds}</div>
                  <p className="text-xs text-muted-foreground">
                    {((healthStats.sickBirds / healthStats.totalBirds) * 100).toFixed(1)}% of total
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Quarantine</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-yellow-600">{healthStats.quarantineBirds}</div>
                  <p className="text-xs text-muted-foreground">Birds in isolation</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Vaccination Rate</CardTitle>
                  <Syringe className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{healthStats.vaccinationRate}%</div>
                  <p className="text-xs text-muted-foreground">Up to date</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Health Alerts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Health Alerts
                </CardTitle>
                <CardDescription>Recent health issues requiring attention</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3 p-3 rounded-lg bg-red-50 border border-red-200">
                  <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-red-800">Vaccination Overdue</p>
                    <p className="text-xs text-red-600 mt-1">
                      Batch B002 - Infectious Bronchitis vaccine is 2 days overdue
                    </p>
                  </div>
                  <Badge variant="destructive">Urgent</Badge>
                </div>

                <div className="flex items-start gap-3 p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                  <Calendar className="h-4 w-4 text-yellow-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-yellow-800">Vaccination Due</p>
                    <p className="text-xs text-yellow-600 mt-1">Batch B001 - Newcastle Disease vaccine due in 2 days</p>
                  </div>
                  <Badge variant="secondary">Due Soon</Badge>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Vaccinations Tab */}
          <TabsContent value="vaccinations" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Vaccination Schedule</h2>
              <AddVaccinationDialog />
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {vaccinations.map((vaccination) => (
                <Card key={vaccination.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{vaccination.vaccine}</CardTitle>
                      <Badge className={getStatusColor(vaccination.status)}>{vaccination.status}</Badge>
                    </div>
                    <CardDescription>Batch {vaccination.batch}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Birds:</span>
                      <span className="font-medium">{vaccination.birdsCount}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Due Date:</span>
                      <span className="font-medium flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {vaccination.dueDate}
                      </span>
                    </div>
                    <div className="flex gap-2 pt-2">
                      <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                        <Syringe className="h-3 w-3 mr-1" />
                        Administer
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                        Reschedule
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Health Records Tab */}
          <TabsContent value="records" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Health Records</h2>
              <AddHealthRecordDialog />
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Recent Health Records</CardTitle>
                <CardDescription>Complete history of health issues and treatments</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Batch</TableHead>
                      <TableHead>Issue</TableHead>
                      <TableHead>Treatment</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Veterinarian</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {healthRecords.map((record) => (
                      <TableRow key={record.id}>
                        <TableCell>{record.date}</TableCell>
                        <TableCell className="font-medium">{record.batch}</TableCell>
                        <TableCell>{record.issue}</TableCell>
                        <TableCell>{record.treatment}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(record.status)}>{record.status}</Badge>
                        </TableCell>
                        <TableCell>{record.veterinarian}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-4">
            <h2 className="text-xl font-semibold">Health Analytics</h2>

            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Mortality Trends
                  </CardTitle>
                  <CardDescription>Monthly mortality rates over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-red-600 mb-2">{healthStats.mortalityRate}%</div>
                  <p className="text-sm text-muted-foreground">Current month</p>
                  <div className="mt-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>December 2023</span>
                      <span>3.1%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>November 2023</span>
                      <span>2.5%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>October 2023</span>
                      <span>2.8%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Health Summary
                  </CardTitle>
                  <CardDescription>Overall health metrics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm">Health Score</span>
                    <span className="font-medium text-green-600">92/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Vaccination Compliance</span>
                    <span className="font-medium">{healthStats.vaccinationRate}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Disease Incidents</span>
                    <span className="font-medium">3 this month</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Recovery Rate</span>
                    <span className="font-medium text-green-600">94%</span>
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
