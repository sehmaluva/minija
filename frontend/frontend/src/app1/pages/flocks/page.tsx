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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../components/ui/dialog"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "../../components/ui/dropdown-menu"
import { Progress } from "../../components/ui/progress"
import { Bird, Plus, MoreHorizontal, Edit, Trash2, Calendar, TrendingUp, AlertCircle } from "lucide-react"
import { useToast } from "../../hooks/use-toast"

interface Flock {
  id: number
  name: string
  breed: string
  farm_name: string
  building_name: string
  current_count: number
  initial_count: number
  age_weeks: number
  status: "active" | "sold" | "deceased"
  health_status: "healthy" | "under_treatment" | "quarantined"
  production_rate: number
  feed_consumption_daily: number
  acquisition_date: string
  expected_production_start: string
}

export default function FlocksPage() {
  const [flocks, setFlocks] = useState<Flock[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingFlock, setEditingFlock] = useState<Flock | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    breed: "",
    farm: "",
    building: "",
    initial_count: "",
    acquisition_date: "",
  })
  const { toast } = useToast()

  // Mock data for demonstration
  const mockFlocks: Flock[] = [
    {
      id: 1,
      name: "Flock A-1",
      breed: "Rhode Island Red",
      farm_name: "Green Valley Farm",
      building_name: "Building A",
      current_count: 850,
      initial_count: 1000,
      age_weeks: 24,
      status: "active",
      health_status: "healthy",
      production_rate: 87.5,
      feed_consumption_daily: 85.2,
      acquisition_date: "2024-01-15",
      expected_production_start: "2024-03-15",
    },
    {
      id: 2,
      name: "Flock B-2",
      breed: "Leghorn",
      farm_name: "Green Valley Farm",
      building_name: "Building B",
      current_count: 920,
      initial_count: 1000,
      age_weeks: 18,
      status: "active",
      health_status: "under_treatment",
      production_rate: 0,
      feed_consumption_daily: 78.5,
      acquisition_date: "2024-02-01",
      expected_production_start: "2024-04-01",
    },
    {
      id: 3,
      name: "Flock C-1",
      breed: "Sussex",
      farm_name: "Sunrise Poultry",
      building_name: "Building A",
      current_count: 450,
      initial_count: 500,
      age_weeks: 32,
      status: "active",
      health_status: "healthy",
      production_rate: 92.1,
      feed_consumption_daily: 42.8,
      acquisition_date: "2023-12-01",
      expected_production_start: "2024-02-01",
    },
  ]

  useEffect(() => {
    const fetchFlocks = async () => {
      try {
        // const data = await apiClient.getFlocks();
        // setFlocks(data.results);
        setFlocks(mockFlocks)
      } catch (error) {
        console.error("Failed to fetch flocks:", error)
        setFlocks(mockFlocks)
      } finally {
        setLoading(false)
      }
    }

    fetchFlocks()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingFlock) {
        // await apiClient.updateFlock(editingFlock.id, formData);
        toast({
          title: "Flock updated",
          description: "Flock information has been updated successfully.",
        })
      } else {
        // await apiClient.createFlock(formData);
        toast({
          title: "Flock created",
          description: "New flock has been created successfully.",
        })
      }
      setDialogOpen(false)
      setEditingFlock(null)
      setFormData({ name: "", breed: "", farm: "", building: "", initial_count: "", acquisition_date: "" })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save flock. Please try again.",
        variant: "destructive",
      })
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800"
      case "sold":
        return "bg-blue-100 text-blue-800"
      case "deceased":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-100 text-green-800"
      case "under_treatment":
        return "bg-yellow-100 text-yellow-800"
      case "quarantined":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const calculateSurvivalRate = (current: number, initial: number) => {
    return ((current / initial) * 100).toFixed(1)
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col lg:pl-72">
          <Header title="Flock Management" subtitle="Monitor and manage your poultry flocks across all farms" />

          <main className="flex-1 overflow-auto p-4 lg:p-8">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Flocks</h2>
                <p className="text-muted-foreground">Track flock health, production, and lifecycle management</p>
              </div>

              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button
                    onClick={() => {
                      setEditingFlock(null)
                      setFormData({
                        name: "",
                        breed: "",
                        farm: "",
                        building: "",
                        initial_count: "",
                        acquisition_date: "",
                      })
                    }}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Flock
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{editingFlock ? "Edit Flock" : "Add New Flock"}</DialogTitle>
                    <DialogDescription>
                      {editingFlock
                        ? "Update the flock information below."
                        : "Create a new flock for tracking and management."}
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">Flock Name</Label>
                        <Input
                          id="name"
                          value={formData.name}
                          onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                          placeholder="e.g., Flock A-1"
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="breed">Breed</Label>
                        <Select
                          value={formData.breed}
                          onValueChange={(value) => setFormData((prev) => ({ ...prev, breed: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select breed" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="rhode_island_red">Rhode Island Red</SelectItem>
                            <SelectItem value="leghorn">Leghorn</SelectItem>
                            <SelectItem value="sussex">Sussex</SelectItem>
                            <SelectItem value="plymouth_rock">Plymouth Rock</SelectItem>
                            <SelectItem value="orpington">Orpington</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="farm">Farm</Label>
                        <Select
                          value={formData.farm}
                          onValueChange={(value) => setFormData((prev) => ({ ...prev, farm: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select farm" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">Green Valley Farm</SelectItem>
                            <SelectItem value="2">Sunrise Poultry</SelectItem>
                            <SelectItem value="3">Heritage Farm</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="building">Building</Label>
                        <Select
                          value={formData.building}
                          onValueChange={(value) => setFormData((prev) => ({ ...prev, building: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select building" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">Building A</SelectItem>
                            <SelectItem value="2">Building B</SelectItem>
                            <SelectItem value="3">Building C</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="initial_count">Initial Count</Label>
                        <Input
                          id="initial_count"
                          type="number"
                          value={formData.initial_count}
                          onChange={(e) => setFormData((prev) => ({ ...prev, initial_count: e.target.value }))}
                          placeholder="1000"
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="acquisition_date">Acquisition Date</Label>
                        <Input
                          id="acquisition_date"
                          type="date"
                          value={formData.acquisition_date}
                          onChange={(e) => setFormData((prev) => ({ ...prev, acquisition_date: e.target.value }))}
                          required
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button type="submit">{editingFlock ? "Update Flock" : "Create Flock"}</Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid gap-6">
              {flocks.map((flock) => (
                <Card key={flock.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <Bird className="h-6 w-6 text-primary" />
                        <div>
                          <CardTitle className="text-xl">{flock.name}</CardTitle>
                          <CardDescription>
                            {flock.breed} • {flock.farm_name} • {flock.building_name}
                          </CardDescription>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(flock.status)}>
                          {flock.status.charAt(0).toUpperCase() + flock.status.slice(1)}
                        </Badge>
                        <Badge className={getHealthStatusColor(flock.health_status)}>
                          {flock.health_status.replace("_", " ").charAt(0).toUpperCase() +
                            flock.health_status.replace("_", " ").slice(1)}
                        </Badge>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>
                              <Edit className="h-4 w-4 mr-2" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive">
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                      {/* Bird Count */}
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Bird className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm font-medium">Bird Count</span>
                        </div>
                        <div className="text-2xl font-bold">{flock.current_count.toLocaleString()}</div>
                        <div className="text-sm text-muted-foreground">
                          of {flock.initial_count.toLocaleString()} initial
                        </div>
                        <Progress
                          value={Number.parseFloat(calculateSurvivalRate(flock.current_count, flock.initial_count))}
                          className="h-2"
                        />
                        <div className="text-xs text-muted-foreground">
                          {calculateSurvivalRate(flock.current_count, flock.initial_count)}% survival rate
                        </div>
                      </div>

                      {/* Age & Production */}
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm font-medium">Age & Production</span>
                        </div>
                        <div className="text-2xl font-bold">{flock.age_weeks} weeks</div>
                        <div className="text-sm text-muted-foreground">
                          {flock.production_rate > 0 ? `${flock.production_rate}% production` : "Pre-production"}
                        </div>
                        {flock.production_rate > 0 && <Progress value={flock.production_rate} className="h-2" />}
                        <div className="text-xs text-muted-foreground">
                          Started: {new Date(flock.acquisition_date).toLocaleDateString()}
                        </div>
                      </div>

                      {/* Feed Consumption */}
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <TrendingUp className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm font-medium">Daily Feed</span>
                        </div>
                        <div className="text-2xl font-bold">{flock.feed_consumption_daily} kg</div>
                        <div className="text-sm text-muted-foreground">
                          {((flock.feed_consumption_daily / flock.current_count) * 1000).toFixed(0)}g per bird
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Weekly: {(flock.feed_consumption_daily * 7).toFixed(1)} kg
                        </div>
                      </div>

                      {/* Health Alerts */}
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm font-medium">Health Status</span>
                        </div>
                        <div className="space-y-2">
                          {flock.health_status === "healthy" && (
                            <div className="text-sm text-green-600">All systems normal</div>
                          )}
                          {flock.health_status === "under_treatment" && (
                            <div className="text-sm text-yellow-600">Treatment in progress</div>
                          )}
                          {flock.health_status === "quarantined" && (
                            <div className="text-sm text-red-600">Quarantine active</div>
                          )}
                          <div className="text-xs text-muted-foreground">Last check: 2 days ago</div>
                        </div>
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex gap-2 mt-6 pt-4 border-t">
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                      <Button variant="outline" size="sm">
                        Health Record
                      </Button>
                      <Button variant="outline" size="sm">
                        Production Log
                      </Button>
                      <Button variant="outline" size="sm">
                        Feed Schedule
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
