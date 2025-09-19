import React from 'react'
import { DollarSign, FileText } from 'lucide-react'

export default function AccountingPage() {
	return (
		<div className="stack">
			<div className="flex items-center justify-between">
				<h2 className="text-2xl font-semibold">Accounting</h2>
				<div className="flex items-center gap-2">
					<button className="btn"><DollarSign className="w-4 h-4"/> New Transaction</button>
				</div>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				<div className="card">
					<div className="flex items-center justify-between">
						<div>
							<div className="text-sm text-gray-500">Total Sales</div>
							<div className="text-xl font-semibold">$12,450</div>
						</div>
						<FileText className="w-8 h-8 text-brand-600" />
					</div>
				</div>

				<div className="card">
					<div className="text-sm text-gray-500">Total Costs</div>
					<div className="text-xl font-semibold">$8,200</div>
				</div>

				<div className="card">
					<div className="text-sm text-gray-500">Net</div>
					<div className="text-xl font-semibold">$4,250</div>
				</div>
			</div>
		</div>
	)
}
