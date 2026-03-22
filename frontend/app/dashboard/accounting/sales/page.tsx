"use client"

import { useEffect, useState } from "react"
import { accountingAPI } from "@/lib/api-functions"
import { Sale, columns } from "./columns"
import { DataTable } from "@/components/ui/data-table"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function SalesPage() {
  const [sales, setSales] = useState<Sale[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    accountingAPI.getSales().then((data) => {
      setSales(data.results || [])
      setLoading(false)
    }).catch(error => {
        console.error("Failed to fetch sales", error);
        setLoading(false);
    });
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Sales</h1>
        <Link href="/dashboard/accounting/sales/new">
            <Button>Create Sale</Button>
        </Link>
      </div>
      <DataTable columns={columns} data={sales} />
    </div>
  )
}
