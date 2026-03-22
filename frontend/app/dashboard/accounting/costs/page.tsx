"use client"

import { useEffect, useState } from "react"
import { accountingAPI } from "@/lib/api-functions"
import { Cost, columns } from "./columns"
import { DataTable } from "@/components/ui/data-table"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function CostsPage() {
  const [costs, setCosts] = useState<Cost[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    accountingAPI.getCosts().then((data) => {
      setCosts(data.results || [])
      setLoading(false)
    }).catch(error => {
        console.error("Failed to fetch costs", error);
        setLoading(false);
    });
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Costs</h1>
        <Link href="/dashboard/accounting/costs/new">
            <Button>Create Cost</Button>
        </Link>
      </div>
      <DataTable columns={columns} data={costs} />
    </div>
  )
}
