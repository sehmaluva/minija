"use client"

export const dynamic = 'force-dynamic'

import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Settings, User, Bell, Shield, Palette } from "lucide-react"
import { useState } from "react"

export default function SettingsPage() {
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    alerts: true,
    reports: true,
  })

  const [profile, setProfile] = useState({
    name: "John Doe",
    email: "john.doe@example.com",
    phone: "+1 (555) 123-4567",
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-balance">Settings</h1>
          <p className="text-muted-foreground text-pretty">Manage your account settings and preferences.</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Profile Settings */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Profile Information
                </CardTitle>
                <CardDescription>Update your personal information and profile details.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="bg-primary rounded-full p-4">
                    <User className="h-8 w-8 text-primary-foreground" />
                  </div>
                  <div>
                    <Button variant="outline" size="sm">Change Photo</Button>
                    <p className="text-sm text-muted-foreground mt-1">JPG, PNG or GIF. Max size 2MB.</p>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      value={profile.name}
                      onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profile.email}
                      onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone</Label>
                    <Input
                      id="phone"
                      value={profile.phone}
                      onChange={(e) => setProfile(prev => ({ ...prev, phone: e.target.value }))}
                    />
                  </div>
                </div>

                <Button>Save Changes</Button>
              </CardContent>
            </Card>

            {/* Notification Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Notification Preferences
                </CardTitle>
                <CardDescription>Choose how you want to be notified about farm activities.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive updates via email</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.email}
                    onChange={(e) =>
                      setNotifications(prev => ({ ...prev, email: e.target.checked }))
                    }
                    className="rounded"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive push notifications in browser</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.push}
                    onChange={(e) =>
                      setNotifications(prev => ({ ...prev, push: e.target.checked }))
                    }
                    className="rounded"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Alert Notifications</Label>
                    <p className="text-sm text-muted-foreground">Get notified about critical alerts</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.alerts}
                    onChange={(e) =>
                      setNotifications(prev => ({ ...prev, alerts: e.target.checked }))
                    }
                    className="rounded"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Report Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive weekly report summaries</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.reports}
                    onChange={(e) =>
                      setNotifications(prev => ({ ...prev, reports: e.target.checked }))
                    }
                    className="rounded"
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Account Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Account Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Account Type</span>
                  <Badge>Premium</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Status</span>
                  <Badge variant="secondary">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Last Login</span>
                  <span className="text-sm text-muted-foreground">Today</span>
                </div>
              </CardContent>
            </Card>

            {/* Theme Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="h-5 w-5" />
                  Appearance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Theme</Label>
                  <div className="grid grid-cols-3 gap-2">
                    <Button variant="outline" size="sm">Light</Button>
                    <Button variant="outline" size="sm">Dark</Button>
                    <Button variant="outline" size="sm">System</Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Danger Zone */}
            <Card className="border-destructive">
              <CardHeader>
                <CardTitle className="text-destructive">Danger Zone</CardTitle>
                <CardDescription>Irreversible actions that affect your account.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button variant="destructive" className="w-full">
                  Delete Account
                </Button>
                <p className="text-xs text-muted-foreground">
                  This action cannot be undone. All your data will be permanently deleted.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}