"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { accountingAPI } from "@/lib/api-functions"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"

export default function CreateTransactionPage() {
  const [description, setDescription] = useState("")
  const [amount, setAmount] = useState(0)
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [transactionType, setTransactionType] = useState<"INCOME" | "EXPENSE">("EXPENSE")
  const [notes, setNotes] = useState("")
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    const transactionData = {
      description,
      amount,
      date,
      transaction_type: transactionType,
      notes,
    }

    try {
      await accountingAPI.createTransaction(transactionData)
      router.push("/dashboard/accounting/transactions")
    } catch (err) {
      setError("Failed to create transaction. Please check your input.")
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Create a New Transaction</CardTitle>
          <CardDescription>Fill in the details of the transaction.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input id="description" value={description} onChange={(e) => setDescription(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="amount">Amount</Label>
                <Input id="amount" type="number" value={amount} onChange={(e) => setAmount(parseFloat(e.target.value))} step="0.01" min="0" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input id="date" type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="transactionType">Transaction Type</Label>
                <Select onValueChange={(value: "INCOME" | "EXPENSE") => setTransactionType(value)} defaultValue={transactionType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="INCOME">Income</SelectItem>
                    <SelectItem value="EXPENSE">Expense</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="mt-6">
              <Label htmlFor="notes">Notes</Label>
              <Textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>

            {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

            <div className="flex justify-end mt-6">
              <Button type="submit">Create Transaction</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
