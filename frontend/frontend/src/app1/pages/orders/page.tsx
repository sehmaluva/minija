import React from 'react'
import { Truck, CalendarPlus } from 'lucide-react'

export default function OrdersPage() {
	return (
		<div className="stack">
			<div className="flex items-center justify-between">
				<h2 className="text-2xl font-semibold">Orders & Reminders</h2>
				<div>
					<button className="btn"><CalendarPlus className="w-4 h-4"/> New Order</button>
				</div>
			</div>

			<div className="card">
				<div className="text-sm text-gray-500">Upcoming Orders</div>
				<div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
					<div className="p-3 border rounded">
						<div className="font-semibold">Chicks - 500 pcs</div>
						<div className="text-sm muted">Delivery: in 3 days</div>
					</div>
					<div className="p-3 border rounded">
						<div className="font-semibold">Feed - Starter 50 bags</div>
						<div className="text-sm muted">Delivery: in 7 days</div>
					</div>
				</div>
			</div>
		</div>
	)
}
