"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Building, Users, MapPin, Plus, Edit, Phone, Mail } from "lucide-react"

export default function FarmPage() {
  const [activeTab, setActiveTab] = useState("coops")

  // Mock data - replace with actual API calls
  const coops = [
    {
      id: 1,
      name: "Coop A",
      capacity: 500,
      currentBirds: 480,
      location: "North Section",
      status: "active",
      lastCleaned: "2024-01-15",
    },
    {
      id: 2,
      name: "Coop B",
      capacity: 750,
      currentBirds: 720,
      location: "East Section",
      status: "active",
      lastCleaned: "2024-01-14",
    },
    {
      id: 3,
      name: "Coop C",
      capacity: 600,
      currentBirds: 0,
      location: "South Section",
      status: "maintenance",
      lastCleaned: "2024-01-10",
    },
  ]

  const staff = [
    {
      id: 1,
      name: "John Smith",
      role: "Farm Manager",
      email: "john@farm.com",
      phone: "+1-555-0123",
      shift: "Morning",
      status: "active",
    },
    {
      id: 2,
      name: "Sarah Johnson",
      role: "Veterinarian",
      email: "sarah@farm.com",
      phone: "+1-555-0124",
      shift: "Full-time",
      status: "active",
    },
    {
      id: 3,
      name: "Mike Wilson",
      role: "Feed Specialist",
      email: "mike@farm.com",
      phone: "+1-555-0125",
      shift: "Evening",
      status: "active",
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800"
      case "maintenance":
        return "bg-yellow-100 text-yellow-800"
      case "inactive":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const AddCoopDialog = () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Coop
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add New Coop</DialogTitle>
          <DialogDescription>Create a new coop for your farm</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="coopName">Coop Name</Label>
            <Input id="coopName" placeholder="Enter coop name" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="capacity">Capacity</Label>
            <Input id="capacity" type="number" placeholder="Maximum birds" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <Input id="location" placeholder="Farm section or coordinates" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea id="description" placeholder="Additional details" />
          </div>
          <Button className="w-full">Create Coop</Button>
        </div>
      </DialogContent>
    </Dialog>
  )

  const AddStaffDialog = () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Staff
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add New Staff Member</DialogTitle>
          <DialogDescription>Add a new team member to your farm</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="staffName">Full Name</Label>
            <Input id="staffName" placeholder="Enter full name" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="manager">Farm Manager</SelectItem>
                <SelectItem value="veterinarian">Veterinarian</SelectItem>
                <SelectItem value="feeder">Feed Specialist</SelectItem>
                <SelectItem value="cleaner">Cleaner</SelectItem>
                <SelectItem value="worker">General Worker</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="Enter email address" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="phone">Phone</Label>
            <Input id="phone" placeholder="Enter phone number" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="shift">Shift</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select shift" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="morning">Morning</SelectItem>
                <SelectItem value="evening">Evening</SelectItem>
                <SelectItem value="night">Night</SelectItem>
                <SelectItem value="fulltime">Full-time</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button className="w-full">Add Staff Member</Button>
        </div>
      </DialogContent>
    </Dialog>
  )

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-balance">Farm Management</h1>
          <p className="text-muted-foreground text-pretty">Manage your coops, barns, and staff members</p>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="coops">Coops & Barns</TabsTrigger>
            <TabsTrigger value="staff">Staff</TabsTrigger>
            <TabsTrigger value="overview">Overview</TabsTrigger>
          </TabsList>

          {/* Coops Tab */}
          <TabsContent value="coops" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Coops & Barns</h2>
              <AddCoopDialog />
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {coops.map((coop) => (
                <Card key={coop.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{coop.name}</CardTitle>
                      <Badge className={getStatusColor(coop.status)}>{coop.status}</Badge>
                    </div>
                    <CardDescription className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {coop.location}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Capacity:</span>
                      <span className="font-medium">{coop.capacity} birds</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Current:</span>
                      <span className="font-medium">{coop.currentBirds} birds</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Occupancy:</span>
                      <span className="font-medium">{((coop.currentBirds / coop.capacity) * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Last Cleaned:</span>
                      <span className="font-medium">{coop.lastCleaned}</span>
                    </div>
                    <div className="flex gap-2 pt-2">
                      <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                        <Edit className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                        <Building className="h-3 w-3 mr-1" />
                        View
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Staff Tab */}
          <TabsContent value="staff" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Staff Members</h2>
              <AddStaffDialog />
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {staff.map((member) => (
                <Card key={member.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{member.name}</CardTitle>
                      <Badge className={getStatusColor(member.status)}>{member.status}</Badge>
                    </div>
                    <CardDescription>{member.role}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="h-3 w-3 text-muted-foreground" />
                      <span>{member.email}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Phone className="h-3 w-3 text-muted-foreground" />
                      <span>{member.phone}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Shift:</span>
                      <span className="font-medium">{member.shift}</span>
                    </div>
                    <div className="flex gap-2 pt-2">
                      <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                        <Edit className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                        <Users className="h-3 w-3 mr-1" />
                        Profile
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <h2 className="text-xl font-semibold">Farm Overview</h2>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Coops</CardTitle>
                  <Building className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{coops.length}</div>
                  <p className="text-xs text-muted-foreground">
                    {coops.filter((c) => c.status === "active").length} active
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Capacity</CardTitle>
                  <Building className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {coops.reduce((sum, coop) => sum + coop.capacity, 0).toLocaleString()}
                  </div>
                  <p className="text-xs text-muted-foreground">birds maximum</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Staff Members</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{staff.length}</div>
                  <p className="text-xs text-muted-foreground">
                    {staff.filter((s) => s.status === "active").length} active
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Occupancy Rate</CardTitle>
                  <Building className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {(
                      (coops.reduce((sum, coop) => sum + coop.currentBirds, 0) /
                        coops.reduce((sum, coop) => sum + coop.capacity, 0)) *
                      100
                    ).toFixed(0)}
                    %
                  </div>
                  <p className="text-xs text-muted-foreground">average across all coops</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
