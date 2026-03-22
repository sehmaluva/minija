"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Save } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import DashboardLayout from "@/components/dashboard-layout"
import { birdsAPI } from "@/lib/api-functions"

export default function NewBatchPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    batch_number: "",
    supplier: "",
    initial_count: "",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await birdsAPI.createBatch({
        ...formData,
        initial_count: Number(formData.initial_count),
        current_count: Number(formData.initial_count),
        status: "active"
      })
      router.push("/dashboard/batches")
    } catch (error) {
      console.error("Error creating batch:", error)
      alert("Failed to create batch. Please check console.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6 max-w-3xl mx-auto">
        <div className="flex items-center space-x-4">
          <Button variant="outline" size="icon" asChild>
            <Link href="/dashboard/batches">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <h2 className="text-3xl font-bold tracking-tight">Create New Batch</h2>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Batch Details</CardTitle>
            <CardDescription>
              Enter the initial details for the new flock.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="batch_number">Batch Number</Label>
                <Input 
                  id="batch_number" 
                  required 
                  placeholder="e.g. BATCH-2026-001"
                  value={formData.batch_number}
                  onChange={(e) => setFormData({...formData, batch_number: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="supplier">Supplier / Hatchery</Label>
                <Input 
                  id="supplier" 
                  required 
                  placeholder="e.g. Premium Hatcheries Inc."
                  value={formData.supplier}
                  onChange={(e) => setFormData({...formData, supplier: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="initial_count">Initial Bird Count</Label>
                <Input 
                  id="initial_count" 
                  type="number" 
                  required 
                  min="1"
                  placeholder="1000"
                  value={formData.initial_count}
                  onChange={(e) => setFormData({...formData, initial_count: e.target.value})}
                />
              </div>

              <div className="pt-4 flex justify-end">
                <Button type="submit" disabled={loading}>
                  <Save className="mr-2 h-4 w-4" />
                  {loading ? "Saving..." : "Save Batch"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
