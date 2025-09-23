"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { BarChart3, Bird, Heart, Home, Menu, Settings, Users, Wheat, LogOut, Feather } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { authAPI } from "@/lib/api-functions"
import { ThemeToggle } from "@/components/theme-toggle"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Birds", href: "/dashboard/birds", icon: Bird },
  { name: "Health", href: "/dashboard/health", icon: Heart },
  { name: "Feed", href: "/dashboard/feed", icon: Wheat },
  { name: "Production", href: "/dashboard/production", icon: BarChart3 },
  { name: "Farm", href: "/dashboard/farm", icon: Users },
  { name: "Settings", href: "/settings", icon: Settings },
]

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local storage and redirect regardless of API response
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
      }
      window.location.href = "/login"
    }
  }

  const SidebarContent = () => (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 px-6 border-b border-sidebar-border">
        <div className="bg-sidebar-primary rounded-full p-2">
          <Feather className="h-5 w-5 text-sidebar-primary-foreground" />
        </div>
        <span className="text-lg font-semibold text-sidebar-foreground">PoultryPro</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
            )}
            onClick={() => setSidebarOpen(false)}
          >
            <item.icon className="h-4 w-4" />
            {item.name}
          </Link>
        ))}
      </nav>

      {/* Theme Toggle */}
      <div className="p-3 border-t border-sidebar-border">
        <div className="flex justify-center">
          <ThemeToggle />
        </div>
      </div>

      {/* Logout */}
      <div className="p-3 border-t border-sidebar-border">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          onClick={handleLogout}
        >
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:bg-sidebar lg:border-r lg:border-sidebar-border">
        <SidebarContent />
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="w-64 p-0 bg-sidebar">
          <SidebarContent />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Mobile Header */}
        <header className="flex h-16 items-center gap-4 border-b border-border bg-background px-4 lg:hidden">
          <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle sidebar</span>
              </Button>
            </SheetTrigger>
          </Sheet>
          <div className="flex items-center gap-2">
            <div className="bg-primary rounded-full p-1.5">
              <Feather className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-semibold">PoultryPro</span>
          </div>
          <div className="ml-auto">
            <ThemeToggle />
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-4 lg:p-6">{children}</main>
      </div>
    </div>
  )
}
