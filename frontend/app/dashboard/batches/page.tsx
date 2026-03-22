"use client"

import { useEffect, useState } from "react"
import { Plus, MoreHorizontal, FileEdit, Trash } from "lucide-react"
import Link from "next/link"
import { format } from "date-fns"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import DashboardLayout from "@/components/dashboard-layout"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { birdsAPI } from "@/lib/api-functions"

export default function BatchesPage() {
  const [batches, setBatches] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchBatches()
  }, [])

  const fetchBatches = async () => {
    try {
      const data = await birdsAPI.getBatches()
      setBatches(Array.isArray(data) ? data : data.results || []) 
    } catch (error) {
      console.error("Error fetching batches:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this batch?")) return;
    try {
      await birdsAPI.deleteBatch(id)
      fetchBatches()
    } catch (error) {
      console.error("Error deleting batch:", error)
    }
  }

  return (
    <DashboardLayout>
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Batches (Flocks)</h2>
          <div className="flex items-center space-x-2">
            <Button asChild>
              <Link href="/dashboard/batches/new">
                <Plus className="mr-2 h-4 w-4" /> Add Batch
              </Link>
            </Button>
          </div>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Active and Historical Batches</CardTitle>
            <CardDescription>
              Manage your poultry flocks, monitor initial counts, and track status.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center p-8">Loading...</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Batch ID</TableHead>
                    <TableHead>Supplier</TableHead>
                    <TableHead>Collection Date</TableHead>
                    <TableHead>Initial Count</TableHead>
                    <TableHead>Current Count</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {batches.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-muted-foreground h-24">
                        No batches found.
                      </TableCell>
                    </TableRow>
                  ) : (
                    batches.map((batch: any) => (
                      <TableRow key={batch.id}>
                        <TableCell className="font-medium">
                          <Link href={`/dashboard/batches/${batch.id}`} className="hover:underline">
                            {batch.batch_number || `Batch #${batch.id}`}
                          </Link>
                        </TableCell>
                        <TableCell>{batch.supplier || 'Unknown'}</TableCell>
                        <TableCell>{batch.collection_date ? format(new Date(batch.collection_date), 'PPP') : 'N/A'}</TableCell>
                        <TableCell>{batch.initial_count}</TableCell>
                        <TableCell>{batch.current_count}</TableCell>
                        <TableCell>
                          <Badge variant={batch.status === "active" ? "default" : "secondary"}>
                            {batch.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" className="h-8 w-8 p-0">
                                <span className="sr-only">Open menu</span>
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Actions</DropdownMenuLabel>
                              <DropdownMenuItem asChild>
                                <Link href={`/dashboard/batches/${batch.id}`}>
                                  <FileEdit className="mr-2 h-4 w-4" /> View Details
                                </Link>
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem 
                                className="text-destructive focus:text-destructive"
                                onClick={() => handleDelete(batch.id)}
                              >
                                <Trash className="mr-2 h-4 w-4" /> Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
