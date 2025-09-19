import React from 'react'
import { BarChart2, Activity } from 'lucide-react'

export default function ForecastPage() {
	return (
		<div className="stack">
			<div className="flex items-center justify-between">
				<h2 className="text-2xl font-semibold">Forecasts & Predictions</h2>
				<div>
					<button className="btn"><Activity className="w-4 h-4"/> Run Prediction</button>
				</div>
			</div>

			<div className="card">
				<div className="text-sm text-gray-500">Next 7 days feed forecast</div>
				<div className="mt-4">
					{/* Placeholder chart area — frontend will render actual recharts/graphs here */}
					<div className="h-40 flex items-center justify-center text-gray-400 border-dashed border-2 border-gray-200 rounded"> <BarChart2 className="w-12 h-12"/> Chart placeholder</div>
				</div>
			</div>
		</div>
	)
}
