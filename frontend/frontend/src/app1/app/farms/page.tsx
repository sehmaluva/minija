"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { ProtectedRoute } from "../../components/auth/protected-route"
import { Sidebar } from "../../components/layout/sidebar"
import { Header } from "../../components/layout/header"
import { Button } from "../../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card"
import { Badge } from "../../components/ui/badge"
import { Input } from "../../components/ui/input"
import { Label } from "../../components/ui/label"
import { Textarea } from "../../components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../components/ui/dialog"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "../../components/ui/dropdown-menu"
import { Building2, Plus, MoreHorizontal, Edit, Trash2, MapPin } from "lucide-react"
import { useToast } from "../../hooks/use-toast"

interface Farm {
  id: number
  name: string
  location: string
  description: string
  total_buildings: number
  total_capacity: number
  current_birds: number
  status: "active" | "inactive" | "maintenance"
  created_at: string
}

export default function FarmsPage() {
  const [farms, setFarms] = useState<Farm[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    location: "",
    description: "",
  })
  const { toast } = useToast()

  // Mock data for demonstration
  const mockFarms: Farm[] = [
    {
      id: 1,
      name: "Green Valley Farm",
      location: "Springfield, IL",
      description: "Main production facility with modern equipment",
      total_buildings: 5,
      total_capacity: 10000,
      current_birds: 8500,
      status: "active",
      created_at: "2024-01-15T10:00:00Z",
    },
    {
      id: 2,
      name: "Sunrise Poultry",
      location: "Madison, WI",
      description: "Organic free-range facility",
      total_buildings: 3,
      total_capacity: 5000,
      current_birds: 4200,
      status: "active",
      created_at: "2024-02-01T10:00:00Z",
    },
    {
      id: 3,
      name: "Heritage Farm",
      location: "Cedar Rapids, IA",
      description: "Specialty breeds and breeding program",
      total_buildings: 2,
      total_capacity: 2000,
      current_birds: 0,
      status: "maintenance",
      created_at: "2024-01-20T10:00:00Z",
    },
  ]

  useEffect(() => {
    const fetchFarms = async () => {
      try {
        // const data = await apiClient.getFarms();
        // setFarms(data.results);
        setFarms(mockFarms)
      } catch (error) {
        console.error("Failed to fetch farms:", error)
        setFarms(mockFarms)
      } finally {
        setLoading(false)
      }
    }

    fetchFarms()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingFarm) {
        // await apiClient.updateFarm(editingFarm.id, formData);
        toast({
          title: "Farm updated",
          description: "Farm information has been updated successfully.",
        })
      } else {
        // await apiClient.createFarm(formData);
        toast({
          title: "Farm created",
          description: "New farm has been created successfully.",
        })
      }
      setDialogOpen(false)
      setEditingFarm(null)
      setFormData({ name: "", location: "", description: "" })
      // Refresh farms list
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save farm. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleEdit = (farm: Farm) => {
    setEditingFarm(farm)
    setFormData({
      name: farm.name,
      location: farm.location,
      description: farm.description,
    })
    setDialogOpen(true)
  }

  const handleDelete = async (farmId: number) => {
    if (confirm("Are you sure you want to delete this farm?")) {
      try {
        // await apiClient.deleteFarm(farmId);
        toast({
          title: "Farm deleted",
          description: "Farm has been deleted successfully.",
        })
        // Refresh farms list
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to delete farm. Please try again.",
          variant: "destructive",
        })
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800"
      case "inactive":
        return "bg-gray-100 text-gray-800"
      case "maintenance":
        return "bg-yellow-100 text-yellow-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col lg:pl-72">
          <Header title="Farm Management" subtitle="Manage your poultry farm locations and facilities" />

          <main className="flex-1 overflow-auto p-4 lg:p-8">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Farms</h2>
                <p className="text-muted-foreground">Manage your farm locations and monitor their status</p>
              </div>

              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button
                    onClick={() => {
                      setEditingFarm(null)
                      setFormData({ name: "", location: "", description: "" })
                    }}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Farm
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{editingFarm ? "Edit Farm" : "Add New Farm"}</DialogTitle>
                    <DialogDescription>
                      {editingFarm
                        ? "Update the farm information below."
                        : "Create a new farm location for your poultry operations."}
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Farm Name</Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                        placeholder="Enter farm name"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="location">Location</Label>
                      <Input
                        id="location"
                        value={formData.location}
                        onChange={(e) => setFormData((prev) => ({ ...prev, location: e.target.value }))}
                        placeholder="City, State"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="description">Description</Label>
                      <Textarea
                        id="description"
                        value={formData.description}
                        onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                        placeholder="Brief description of the farm"
                        rows={3}
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button type="submit">{editingFarm ? "Update Farm" : "Create Farm"}</Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {farms.map((farm) => (
                <Card key={farm.id} className="relative">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-5 w-5 text-primary" />
                        <CardTitle className="text-lg">{farm.name}</CardTitle>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleEdit(farm)}>
                            <Edit className="h-4 w-4 mr-2" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleDelete(farm.id)} className="text-destructive">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <MapPin className="h-3 w-3" />
                      {farm.location}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">{farm.description}</p>

                    <div className="flex justify-between items-center">
                      <Badge className={getStatusColor(farm.status)}>
                        {farm.status.charAt(0).toUpperCase() + farm.status.slice(1)}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(farm.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 pt-2 border-t">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary">{farm.total_buildings}</div>
                        <div className="text-xs text-muted-foreground">Buildings</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary">{farm.current_birds.toLocaleString()}</div>
                        <div className="text-xs text-muted-foreground">
                          of {farm.total_capacity.toLocaleString()} birds
                        </div>
                      </div>
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
