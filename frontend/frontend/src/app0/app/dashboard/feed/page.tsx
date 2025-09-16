"use client"

import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Wheat, Plus, AlertTriangle, Calendar, Package } from "lucide-react"

export default function FeedPage() {
  // Mock data - replace with actual API calls
  const feedInventory = [
    {
      id: 1,
      type: "Layer Feed",
      brand: "Premium Poultry",
      quantity: 2500,
      unit: "kg",
      lowStock: 500,
      expiryDate: "2024-03-15",
      cost: 1.2,
    },
    {
      id: 2,
      type: "Starter Feed",
      brand: "ChickStart Pro",
      quantity: 150,
      unit: "kg",
      lowStock: 200,
      expiryDate: "2024-02-28",
      cost: 1.45,
    },
    {
      id: 3,
      type: "Grower Feed",
      brand: "GrowStrong",
      quantity: 800,
      unit: "kg",
      lowStock: 300,
      expiryDate: "2024-04-10",
      cost: 1.35,
    },
  ]

  const feedingSchedule = [
    {
      id: 1,
      batch: "B001",
      feedType: "Layer Feed",
      amount: 45,
      frequency: "2x daily",
      nextFeeding: "2024-01-16 06:00",
    },
    {
      id: 2,
      batch: "B002",
      feedType: "Layer Feed",
      amount: 68,
      frequency: "2x daily",
      nextFeeding: "2024-01-16 06:00",
    },
    {
      id: 3,
      batch: "B003",
      feedType: "Grower Feed",
      amount: 25,
      frequency: "3x daily",
      nextFeeding: "2024-01-16 06:00",
    },
  ]

  const getStockStatus = (quantity: number, lowStock: number) => {
    if (quantity <= lowStock) return { status: "low", color: "bg-red-100 text-red-800" }
    if (quantity <= lowStock * 1.5) return { status: "medium", color: "bg-yellow-100 text-yellow-800" }
    return { status: "good", color: "bg-green-100 text-green-800" }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-balance">Feed Management</h1>
          <p className="text-muted-foreground text-pretty">
            Manage feed inventory, schedules, and consumption tracking
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Feed Stock</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3,450 kg</div>
              <p className="text-xs text-muted-foreground">across all types</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Daily Consumption</CardTitle>
              <Wheat className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">138 kg</div>
              <p className="text-xs text-muted-foreground">average per day</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Low Stock Items</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">1</div>
              <p className="text-xs text-muted-foreground">needs restocking</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Monthly Cost</CardTitle>
              <Wheat className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">$4,200</div>
              <p className="text-xs text-muted-foreground">feed expenses</p>
            </CardContent>
          </Card>
        </div>

        {/* Feed Inventory */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Feed Inventory</CardTitle>
                <CardDescription>Current stock levels and status</CardDescription>
              </div>
              <Dialog>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Feed Stock
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add Feed Stock</DialogTitle>
                    <DialogDescription>Add new feed inventory</DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="feedType">Feed Type</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select feed type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="layer">Layer Feed</SelectItem>
                          <SelectItem value="starter">Starter Feed</SelectItem>
                          <SelectItem value="grower">Grower Feed</SelectItem>
                          <SelectItem value="finisher">Finisher Feed</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="brand">Brand</Label>
                      <Input id="brand" placeholder="Feed brand name" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="quantity">Quantity (kg)</Label>
                      <Input id="quantity" type="number" placeholder="Amount in kg" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="cost">Cost per kg ($)</Label>
                      <Input id="cost" type="number" step="0.01" placeholder="Cost per kilogram" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="expiry">Expiry Date</Label>
                      <Input id="expiry" type="date" />
                    </div>
                    <Button className="w-full">Add to Inventory</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Feed Type</TableHead>
                  <TableHead>Brand</TableHead>
                  <TableHead>Quantity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Expiry Date</TableHead>
                  <TableHead>Cost/kg</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {feedInventory.map((feed) => {
                  const stockStatus = getStockStatus(feed.quantity, feed.lowStock)
                  return (
                    <TableRow key={feed.id}>
                      <TableCell className="font-medium">{feed.type}</TableCell>
                      <TableCell>{feed.brand}</TableCell>
                      <TableCell>
                        {feed.quantity} {feed.unit}
                      </TableCell>
                      <TableCell>
                        <Badge className={stockStatus.color}>{stockStatus.status}</Badge>
                      </TableCell>
                      <TableCell className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {feed.expiryDate}
                      </TableCell>
                      <TableCell>${feed.cost}</TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Feeding Schedule */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Feeding Schedule</CardTitle>
                <CardDescription>Daily feeding schedule for all batches</CardDescription>
              </div>
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Schedule
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add Feeding Schedule</DialogTitle>
                    <DialogDescription>Create feeding schedule for a batch</DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="batch">Batch</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select batch" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="b001">Batch B001</SelectItem>
                          <SelectItem value="b002">Batch B002</SelectItem>
                          <SelectItem value="b003">Batch B003</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="feedType">Feed Type</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select feed type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="layer">Layer Feed</SelectItem>
                          <SelectItem value="starter">Starter Feed</SelectItem>
                          <SelectItem value="grower">Grower Feed</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="amount">Amount per feeding (kg)</Label>
                      <Input id="amount" type="number" placeholder="Amount in kg" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="frequency">Frequency</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select frequency" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1x">Once daily</SelectItem>
                          <SelectItem value="2x">Twice daily</SelectItem>
                          <SelectItem value="3x">Three times daily</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <Button className="w-full">Create Schedule</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Batch</TableHead>
                  <TableHead>Feed Type</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Frequency</TableHead>
                  <TableHead>Next Feeding</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {feedingSchedule.map((schedule) => (
                  <TableRow key={schedule.id}>
                    <TableCell className="font-medium">{schedule.batch}</TableCell>
                    <TableCell>{schedule.feedType}</TableCell>
                    <TableCell>{schedule.amount} kg</TableCell>
                    <TableCell>{schedule.frequency}</TableCell>
                    <TableCell>{new Date(schedule.nextFeeding).toLocaleString()}</TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline">
                        Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
