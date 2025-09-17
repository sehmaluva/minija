"use client"

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
import { Textarea } from "../../components/ui/textarea"
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
import { Calendar } from "../../components/ui/calendar"
import { Heart, Plus, CalendarIcon, Syringe, Pill, AlertTriangle, Clock } from "lucide-react"
import { useToast } from "../../hooks/use-toast"

interface HealthRecord {
  id: number
  flock_name: string
  record_type: "vaccination" | "medication" | "checkup" | "treatment"
  title: string
  description: string
  administered_by: string
  date_administered: string
  next_due_date?: string
  status: "completed" | "scheduled" | "overdue"
  birds_affected: number
  cost: number
}

interface VaccinationSchedule {
  id: number
  vaccine_name: string
  flock_name: string
  scheduled_date: string
  status: "pending" | "completed" | "overdue"
  birds_count: number
  notes: string
}

export default function HealthPage() {
  const [healthRecords, setHealthRecords] = useState<HealthRecord[]>([])
  const [vaccinationSchedule, setVaccinationSchedule] = useState<VaccinationSchedule[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedDate, setSelectedDate] = useState<Date>()
  const [formData, setFormData] = useState({
    flock: "",
    record_type: "",
    title: "",
    description: "",
    date_administered: "",
    next_due_date: "",
    birds_affected: "",
    cost: "",
  })
  const { toast } = useToast()

  // Mock data for demonstration
  const mockHealthRecords: HealthRecord[] = [
    {
      id: 1,
      flock_name: "Flock A-1",
      record_type: "vaccination",
      title: "Newcastle Disease Vaccine",
      description: "Routine vaccination against Newcastle disease",
      administered_by: "Dr. Smith",
      date_administered: "2024-01-15",
      next_due_date: "2024-04-15",
      status: "completed",
      birds_affected: 850,
      cost: 125.5,
    },
    {
      id: 2,
      flock_name: "Flock B-2",
      record_type: "medication",
      title: "Antibiotic Treatment",
      description: "Treatment for respiratory infection",
      administered_by: "Farm Manager",
      date_administered: "2024-02-10",
      status: "completed",
      birds_affected: 45,
      cost: 89.25,
    },
    {
      id: 3,
      flock_name: "Flock C-1",
      record_type: "checkup",
      title: "Monthly Health Inspection",
      description: "Routine health check and assessment",
      administered_by: "Dr. Johnson",
      date_administered: "2024-02-20",
      next_due_date: "2024-03-20",
      status: "completed",
      birds_affected: 450,
      cost: 75.0,
    },
  ]

  const mockVaccinationSchedule: VaccinationSchedule[] = [
    {
      id: 1,
      vaccine_name: "Infectious Bronchitis",
      flock_name: "Flock A-1",
      scheduled_date: "2024-03-15",
      status: "pending",
      birds_count: 850,
      notes: "Second dose required",
    },
    {
      id: 2,
      vaccine_name: "Avian Influenza",
      flock_name: "Flock B-2",
      scheduled_date: "2024-03-10",
      status: "overdue",
      birds_count: 920,
      notes: "Urgent - overdue by 5 days",
    },
    {
      id: 3,
      vaccine_name: "Fowl Pox",
      flock_name: "Flock C-1",
      scheduled_date: "2024-03-25",
      status: "pending",
      birds_count: 450,
      notes: "First vaccination",
    },
  ]

  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        // const records = await apiClient.getHealthRecords();
        // const schedule = await apiClient.getVaccinationSchedule();
        setHealthRecords(mockHealthRecords)
        setVaccinationSchedule(mockVaccinationSchedule)
      } catch (error) {
        console.error("Failed to fetch health data:", error)
        setHealthRecords(mockHealthRecords)
        setVaccinationSchedule(mockVaccinationSchedule)
      } finally {
        setLoading(false)
      }
    }

    fetchHealthData()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // await apiClient.createHealthRecord(formData);
      toast({
        title: "Health record added",
        description: "Health record has been created successfully.",
      })
      setDialogOpen(false)
      setFormData({
        flock: "",
        record_type: "",
        title: "",
        description: "",
        date_administered: "",
        next_due_date: "",
        birds_affected: "",
        cost: "",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create health record. Please try again.",
        variant: "destructive",
      })
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800"
      case "scheduled":
      case "pending":
        return "bg-blue-100 text-blue-800"
      case "overdue":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getRecordTypeIcon = (type: string) => {
    switch (type) {
      case "vaccination":
        return <Syringe className="h-4 w-4" />
      case "medication":
        return <Pill className="h-4 w-4" />
      case "checkup":
        return <Heart className="h-4 w-4" />
      case "treatment":
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Heart className="h-4 w-4" />
    }
  }

  const upcomingVaccinations = vaccinationSchedule.filter((v) => v.status === "pending" || v.status === "overdue")
  const overdueCount = vaccinationSchedule.filter((v) => v.status === "overdue").length

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col lg:pl-72">
          <Header
            title="Health Management"
            subtitle="Track vaccinations, treatments, and health records for your flocks"
          />

          <main className="flex-1 overflow-auto p-4 lg:p-8">
            {/* Health Overview Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Records</CardTitle>
                  <Heart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{healthRecords.length}</div>
                  <p className="text-xs text-muted-foreground">This month</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Upcoming Vaccinations</CardTitle>
                  <Syringe className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{upcomingVaccinations.length}</div>
                  <p className="text-xs text-muted-foreground">Next 30 days</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Overdue Items</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{overdueCount}</div>
                  <p className="text-xs text-muted-foreground">Requires attention</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Health Cost</CardTitle>
                  <Pill className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    ${healthRecords.reduce((sum, record) => sum + record.cost, 0).toFixed(2)}
                  </div>
                  <p className="text-xs text-muted-foreground">This month</p>
                </CardContent>
              </Card>
            </div>

            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Health Records</h2>
                <p className="text-muted-foreground">Manage health records, vaccinations, and treatment schedules</p>
              </div>

              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Health Record
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Add Health Record</DialogTitle>
                    <DialogDescription>
                      Create a new health record for vaccination, medication, or treatment.
                    </DialogDescription>
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
                        <Label htmlFor="record_type">Record Type</Label>
                        <Select
                          value={formData.record_type}
                          onValueChange={(value) => setFormData((prev) => ({ ...prev, record_type: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="vaccination">Vaccination</SelectItem>
                            <SelectItem value="medication">Medication</SelectItem>
                            <SelectItem value="checkup">Health Checkup</SelectItem>
                            <SelectItem value="treatment">Treatment</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="title">Title</Label>
                      <Input
                        id="title"
                        value={formData.title}
                        onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                        placeholder="e.g., Newcastle Disease Vaccine"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="description">Description</Label>
                      <Textarea
                        id="description"
                        value={formData.description}
                        onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                        placeholder="Detailed description of the procedure"
                        rows={3}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="date_administered">Date Administered</Label>
                        <Input
                          id="date_administered"
                          type="date"
                          value={formData.date_administered}
                          onChange={(e) => setFormData((prev) => ({ ...prev, date_administered: e.target.value }))}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="next_due_date">Next Due Date (Optional)</Label>
                        <Input
                          id="next_due_date"
                          type="date"
                          value={formData.next_due_date}
                          onChange={(e) => setFormData((prev) => ({ ...prev, next_due_date: e.target.value }))}
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="birds_affected">Birds Affected</Label>
                        <Input
                          id="birds_affected"
                          type="number"
                          value={formData.birds_affected}
                          onChange={(e) => setFormData((prev) => ({ ...prev, birds_affected: e.target.value }))}
                          placeholder="850"
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="cost">Cost ($)</Label>
                        <Input
                          id="cost"
                          type="number"
                          step="0.01"
                          value={formData.cost}
                          onChange={(e) => setFormData((prev) => ({ ...prev, cost: e.target.value }))}
                          placeholder="125.50"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button type="submit">Create Record</Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <Tabs defaultValue="records" className="space-y-4">
              <TabsList>
                <TabsTrigger value="records">Health Records</TabsTrigger>
                <TabsTrigger value="schedule">Vaccination Schedule</TabsTrigger>
                <TabsTrigger value="calendar">Calendar View</TabsTrigger>
              </TabsList>

              <TabsContent value="records" className="space-y-4">
                <div className="grid gap-4">
                  {healthRecords.map((record) => (
                    <Card key={record.id}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            {getRecordTypeIcon(record.record_type)}
                            <div>
                              <CardTitle className="text-lg">{record.title}</CardTitle>
                              <CardDescription>
                                {record.flock_name} • {record.administered_by}
                              </CardDescription>
                            </div>
                          </div>
                          <Badge className={getStatusColor(record.status)}>
                            {record.status.charAt(0).toUpperCase() + record.status.slice(1)}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                          <div>
                            <div className="text-sm font-medium">Date Administered</div>
                            <div className="text-sm text-muted-foreground">
                              {new Date(record.date_administered).toLocaleDateString()}
                            </div>
                          </div>
                          <div>
                            <div className="text-sm font-medium">Birds Affected</div>
                            <div className="text-sm text-muted-foreground">
                              {record.birds_affected.toLocaleString()}
                            </div>
                          </div>
                          <div>
                            <div className="text-sm font-medium">Cost</div>
                            <div className="text-sm text-muted-foreground">${record.cost.toFixed(2)}</div>
                          </div>
                          {record.next_due_date && (
                            <div>
                              <div className="text-sm font-medium">Next Due</div>
                              <div className="text-sm text-muted-foreground">
                                {new Date(record.next_due_date).toLocaleDateString()}
                              </div>
                            </div>
                          )}
                        </div>
                        {record.description && (
                          <div className="mt-4 pt-4 border-t">
                            <div className="text-sm text-muted-foreground">{record.description}</div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="schedule" className="space-y-4">
                <div className="grid gap-4">
                  {vaccinationSchedule.map((vaccination) => (
                    <Card key={vaccination.id}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <Syringe className="h-5 w-5 text-primary" />
                            <div>
                              <CardTitle className="text-lg">{vaccination.vaccine_name}</CardTitle>
                              <CardDescription>
                                {vaccination.flock_name} • {vaccination.birds_count.toLocaleString()} birds
                              </CardDescription>
                            </div>
                          </div>
                          <Badge className={getStatusColor(vaccination.status)}>
                            {vaccination.status.charAt(0).toUpperCase() + vaccination.status.slice(1)}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                              <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm">
                                {new Date(vaccination.scheduled_date).toLocaleDateString()}
                              </span>
                            </div>
                            {vaccination.status === "overdue" && (
                              <div className="flex items-center gap-2 text-red-600">
                                <Clock className="h-4 w-4" />
                                <span className="text-sm font-medium">Overdue</span>
                              </div>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <Button variant="outline" size="sm">
                              Reschedule
                            </Button>
                            <Button size="sm">Mark Complete</Button>
                          </div>
                        </div>
                        {vaccination.notes && (
                          <div className="mt-4 pt-4 border-t">
                            <div className="text-sm text-muted-foreground">{vaccination.notes}</div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="calendar" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Health Calendar</CardTitle>
                    <CardDescription>View upcoming vaccinations and health activities</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Calendar
                      mode="single"
                      selected={selectedDate}
                      onSelect={setSelectedDate}
                      className="rounded-md border"
                    />
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
