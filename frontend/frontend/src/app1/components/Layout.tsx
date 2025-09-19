import React, { useState } from 'react'
import { Menu, Home, Box, DollarSign, Truck, BarChart2 } from 'lucide-react'

const Header: React.FC = () => {
  const [open, setOpen] = useState(false)

  return (
    <header className="bg-gradient-to-r from-brand-600 to-brand-500 text-white">
      <div className="container flex items-center justify-between h-16">
        <div className="flex items-center gap-3">
          <Home className="h-6 w-6 text-white" />
          <h1 className="text-lg font-semibold tracking-tight">MiniJa Broilers</h1>
        </div>

        <nav className="hidden md:flex items-center gap-6">
          <a className="flex items-center gap-2 hover:underline" href="/dashboard"><BarChart2 className="w-4 h-4"/> Dashboard</a>
          <a className="flex items-center gap-2 hover:underline" href="/orders"><Truck className="w-4 h-4"/> Orders</a>
          <a className="flex items-center gap-2 hover:underline" href="/accounting"><DollarSign className="w-4 h-4"/> Accounting</a>
          <a className="flex items-center gap-2 hover:underline" href="/forecast"><Box className="w-4 h-4"/> Forecast</a>
        </nav>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center text-sm text-white/90">Small-scale broiler manager</div>
          <button onClick={() => setOpen(v => !v)} className="md:hidden p-2 rounded bg-white/10 hover:bg-white/20">
            <Menu className="h-5 w-5 text-white" />
          </button>
        </div>
      </div>

      {/* mobile menu */}
      {open && (
        <div className="md:hidden bg-brand-50 text-brand-900 border-t">
          <div className="flex flex-col gap-2 p-4">
            <a className="flex items-center gap-2 p-2 rounded hover:bg-brand-100" href="/dashboard">Dashboard</a>
            <a className="flex items-center gap-2 p-2 rounded hover:bg-brand-100" href="/orders">Orders</a>
            <a className="flex items-center gap-2 p-2 rounded hover:bg-brand-100" href="/accounting">Accounting</a>
            <a className="flex items-center gap-2 p-2 rounded hover:bg-brand-100" href="/forecast">Forecast</a>
          </div>
        </div>
      )}
    </header>
  )
}

const Footer: React.FC = () => (
  <footer className="bg-white border-t mt-8">
    <div className="container py-6 text-sm text-gray-600 flex items-center justify-between">
      <div>© {new Date().getFullYear()} MiniJa — Broiler manager</div>
      <div className="text-xs text-gray-500">Built for small-scale production</div>
    </div>
  </footer>
)

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-white text-gray-800">
      <Header />
      <main className="container py-6">{children}</main>
      <Footer />
    </div>
  )
}

export default Layout
