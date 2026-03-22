"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { accountingAPI } from "@/lib/api-functions"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

export default function CreateSalePage() {
  const [customerName, setCustomerName] = useState("")
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [notes, setNotes] = useState("")
  const [saleItems, setSaleItems] = useState([{ item: "", quantity: 1, unit_price: 0 }])
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const handleItemChange = (index: number, field: string, value: any) => {
    const newItems = [...saleItems]
    newItems[index] = { ...newItems[index], [field]: value }
    setSaleItems(newItems)
  }

  const addItem = () => {
    setSaleItems([...saleItems, { item: "", quantity: 1, unit_price: 0 }])
  }

  const removeItem = (index: number) => {
    const newItems = saleItems.filter((_, i) => i !== index)
    setSaleItems(newItems)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    const saleData = {
      customer_name: customerName,
      date,
      notes,
      sale_items: saleItems,
    }

    try {
      await accountingAPI.createSale(saleData)
      router.push("/dashboard/accounting/sales")
    } catch (err) {
      setError("Failed to create sale. Please check your input.")
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Create a New Sale</CardTitle>
          <CardDescription>Fill in the details of the sale.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="customerName">Customer Name</Label>
                <Input id="customerName" value={customerName} onChange={(e) => setCustomerName(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input id="date" type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
              </div>
            </div>

            <div className="mt-6">
              <Label>Sale Items</Label>
              {saleItems.map((item, index) => (
                <div key={index} className="flex items-center gap-4 mt-2">
                  <Input placeholder="Item description" value={item.item} onChange={(e) => handleItemChange(index, "item", e.target.value)} required />
                  <Input type="number" placeholder="Quantity" value={item.quantity} onChange={(e) => handleItemChange(index, "quantity", parseInt(e.target.value))} min="1" required />
                  <Input type="number" placeholder="Unit Price" value={item.unit_price} onChange={(e) => handleItemChange(index, "unit_price", parseFloat(e.target.value))} step="0.01" min="0" required />
                  <Button type="button" variant="destructive" onClick={() => removeItem(index)}>Remove</Button>
                </div>
              ))}
              <Button type="button" variant="outline" onClick={addItem} className="mt-2">Add Item</Button>
            </div>

            <div className="mt-6">
              <Label htmlFor="notes">Notes</Label>
              <Textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>

            {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

            <div className="flex justify-end mt-6">
              <Button type="submit">Create Sale</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
