"use client"

import { useEffect, useState } from "react"
import { accountingAPI } from "@/lib/api-functions"
import { Transaction, columns } from "./columns"
import { DataTable } from "@/components/ui/data-table"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    accountingAPI.getTransactions().then((data) => {
      setTransactions(data.results || [])
      setLoading(false)
    }).catch(error => {
        console.error("Failed to fetch transactions", error);
        setLoading(false);
    });
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Transactions</h1>
        <Link href="/dashboard/accounting/transactions/new">
            <Button>Create Transaction</Button>
        </Link>
      </div>
      <DataTable columns={columns} data={transactions} />
    </div>
  )
}
