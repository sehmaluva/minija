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
import { Plus, Search, Filter, Calendar, MapPin, Eye, Edit } from "lucide-react"

export default function BirdsPage() {
  const [activeTab, setActiveTab] = useState("batches")
  const [searchTerm, setSearchTerm] = useState("")

  // Mock data - replace with actual API calls
  const batches = [
    {
      id: "B001",
      breed: "Rhode Island Red",
      count: 500,
      age: 12,
      location: "Coop A",
      status: "healthy",
      hatchDate: "2024-01-03",
      mortality: 2,
    },
    {
      id: "B002",
      breed: "Leghorn",
      count: 750,
      age: 8,
      location: "Coop B",
      status: "healthy",
      hatchDate: "2024-01-07",
      mortality: 1,
    },
    {
      id: "B003",
      breed: "Sussex",
      count: 300,
      age: 20,
      location: "Coop C",
      status: "monitoring",
      hatchDate: "2023-12-26",
      mortality: 5,
    },
  ]

  const breeds = [
    {
      id: 1,
      name: "Rhode Island Red",
      type: "Dual Purpose",
      eggColor: "Brown",
      avgWeight: "3.2 kg",
      eggProduction: "250-300/year",
      characteristics: "Hardy, good foragers",
    },
    {
      id: 2,
      name: "Leghorn",
      type: "Egg Layer",
      eggColor: "White",
      avgWeight: "2.5 kg",
      eggProduction: "280-320/year",
      characteristics: "High egg production, active",
    },
    {
      id: 3,
      name: "Sussex",
      type: "Dual Purpose",
      eggColor: "Light Brown",
      avgWeight: "3.6 kg",
      eggProduction: "200-250/year",
      characteristics: "Docile, good mothers",
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-100 text-green-800"
      case "monitoring":
        return "bg-yellow-100 text-yellow-800"
      case "sick":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const AddBatchDialog = () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Batch
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add New Batch</DialogTitle>
          <DialogDescription>Register a new batch of birds</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="batchId">Batch ID</Label>
            <Input id="batchId" placeholder="e.g., B004" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="breed">Breed</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select breed" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="rhode-island-red">Rhode Island Red</SelectItem>
                <SelectItem value="leghorn">Leghorn</SelectItem>
                <SelectItem value="sussex">Sussex</SelectItem>
                <SelectItem value="plymouth-rock">Plymouth Rock</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="count">Bird Count</Label>
            <Input id="count" type="number" placeholder="Number of birds" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="hatchDate">Hatch Date</Label>
            <Input id="hatchDate" type="date" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select coop" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="coop-a">Coop A</SelectItem>
                <SelectItem value="coop-b">Coop B</SelectItem>
                <SelectItem value="coop-c">Coop C</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button className="w-full">Add Batch</Button>
        </div>
      </DialogContent>
    </Dialog>
  )

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-balance">Bird Management</h1>
          <p className="text-muted-foreground text-pretty">Track and manage your bird batches and breeds</p>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="batches">Batches</TabsTrigger>
            <TabsTrigger value="breeds">Breeds</TabsTrigger>
            <TabsTrigger value="individual">Individual Birds</TabsTrigger>
          </TabsList>

          {/* Batches Tab */}
          <TabsContent value="batches" className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4 justify-between">
              <div className="flex gap-2">
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search batches..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                </Button>
              </div>
              <AddBatchDialog />
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {batches.map((batch) => (
                <Card key={batch.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">Batch {batch.id}</CardTitle>
                      <Badge className={getStatusColor(batch.status)}>{batch.status}</Badge>
                    </div>
                    <CardDescription>{batch.breed}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Count:</span>
                      <span className="font-medium">{batch.count} birds</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Age:</span>
                      <span className="font-medium">{batch.age} weeks</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Location:</span>
                      <span className="font-medium flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {batch.location}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Mortality:</span>
                      <span className="font-medium">{batch.mortality} birds</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Hatch Date:</span>
                      <span className="font-medium flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {batch.hatchDate}
                      </span>
                    </div>
                    <div className="flex gap-2 pt-2">
                      <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                        <Eye className="h-3 w-3 mr-1" />
                        View
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                        <Edit className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Breeds Tab */}
          <TabsContent value="breeds" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Breed Information</h2>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Breed
              </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {breeds.map((breed) => (
                <Card key={breed.id}>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">{breed.name}</CardTitle>
                    <CardDescription>{breed.type}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Egg Color:</span>
                      <span className="font-medium">{breed.eggColor}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Avg Weight:</span>
                      <span className="font-medium">{breed.avgWeight}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Egg Production:</span>
                      <span className="font-medium">{breed.eggProduction}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-muted-foreground">Characteristics:</span>
                      <p className="font-medium mt-1">{breed.characteristics}</p>
                    </div>
                    <Button size="sm" variant="outline" className="w-full bg-transparent">
                      <Eye className="h-3 w-3 mr-1" />
                      View Details
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Individual Birds Tab */}
          <TabsContent value="individual" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Individual Bird Records</h2>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Bird
              </Button>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Bird Registry</CardTitle>
                <CardDescription>Individual bird tracking and records</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ID</TableHead>
                      <TableHead>Batch</TableHead>
                      <TableHead>Breed</TableHead>
                      <TableHead>Age</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell className="font-medium">B001-001</TableCell>
                      <TableCell>B001</TableCell>
                      <TableCell>Rhode Island Red</TableCell>
                      <TableCell>12 weeks</TableCell>
                      <TableCell>
                        <Badge className="bg-green-100 text-green-800">Healthy</Badge>
                      </TableCell>
                      <TableCell>Coop A</TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">B001-002</TableCell>
                      <TableCell>B001</TableCell>
                      <TableCell>Rhode Island Red</TableCell>
                      <TableCell>12 weeks</TableCell>
                      <TableCell>
                        <Badge className="bg-green-100 text-green-800">Healthy</Badge>
                      </TableCell>
                      <TableCell>Coop A</TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">B002-001</TableCell>
                      <TableCell>B002</TableCell>
                      <TableCell>Leghorn</TableCell>
                      <TableCell>8 weeks</TableCell>
                      <TableCell>
                        <Badge className="bg-yellow-100 text-yellow-800">Monitoring</Badge>
                      </TableCell>
                      <TableCell>Coop B</TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
