import { Link, useLocation } from "react-router-dom"
import { cn } from "../../lib/utils"
import { Button } from "../ui/button"
import { ScrollArea } from "../ui/scroll-area"
import { Sheet, SheetContent, SheetTrigger } from "../ui/sheet"
import { Home, Building2, Bird, Heart, TrendingUp, BarChart3, Settings, Menu, LogOut, Truck, DollarSign } from "lucide-react"
import { useAuth } from "../../contexts/auth-context"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Flocks", href: "/flocks", icon: Bird },
  { name: "Production", href: "/production", icon: TrendingUp },
  { name: "Orders", href: "/orders", icon: Truck },
  { name: "Accounting", href: "/accounting", icon: DollarSign },
  { name: "Forecast", href: "/forecast", icon: BarChart3 },
  { name: "Reports", href: "/reports", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
]

interface SidebarProps {
  className?: string
}

function SidebarContent({ className }: SidebarProps) {
  const location = useLocation()
  const { user, logout } = useAuth()

  return (
    <div className={cn("flex h-full flex-col bg-sidebar", className)}>
      <div className="flex h-14 items-center border-b border-sidebar-border px-4">
        <div className="flex items-center gap-2">
          <Bird className="h-6 w-6 text-sidebar-primary" />
          <span className="font-semibold text-sidebar-foreground">PoultryPro</span>
        </div>
      </div>

      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link key={item.name} to={item.href}>
                <Button
                  variant={isActive ? "default" : "ghost"}
                  className={cn(
                    "w-full justify-start gap-3",
                    isActive
                      ? "bg-sidebar-primary text-sidebar-primary-foreground"
                      : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.name}
                </Button>
              </Link>
            )
          })}
        </nav>
      </ScrollArea>

      <div className="border-t border-sidebar-border p-4">
        <div className="mb-3 text-sm text-sidebar-foreground">
          <div className="font-medium">
            {user?.first_name} {user?.last_name}
          </div>
          <div className="text-xs text-muted-foreground">{user?.email}</div>
        </div>
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-sidebar-foreground hover:bg-sidebar-accent"
          onClick={logout}
        >
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </div>
  )
}

export function Sidebar() {
  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <SidebarContent />
      </div>

      {/* Mobile Sidebar */}
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="lg:hidden fixed top-4 left-4 z-40">
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-72 p-0">
          <SidebarContent />
        </SheetContent>
      </Sheet>
    </>
  )
}
