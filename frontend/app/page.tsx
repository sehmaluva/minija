"use client"

import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Feather, BarChart3, Shield, Users } from "lucide-react"
import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-green-200">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary rounded-full p-2">
              <Feather className="h-6 w-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">PoultryPro</span>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-balance mb-6">
            Modern Poultry Farm
            <span className="text-primary"> Management</span>
          </h1>
          <p className="text-xl text-muted-foreground text-pretty max-w-2xl mx-auto mb-8">
            Streamline your poultry operations with comprehensive bird tracking, health monitoring, and production
            analytics in one powerful platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/register">Start Free Trial</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="text-center">
            <CardHeader>
              <div className="bg-primary/10 rounded-full p-3 w-fit mx-auto mb-4">
                <BarChart3 className="h-8 w-8 text-primary" />
              </div>
              <CardTitle>Production Analytics</CardTitle>
              <CardDescription>
                Track egg production, feed consumption, and growth rates with detailed analytics and reporting.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <div className="bg-primary/10 rounded-full p-3 w-fit mx-auto mb-4">
                <Shield className="h-8 w-8 text-primary" />
              </div>
              <CardTitle>Health Monitoring</CardTitle>
              <CardDescription>
                Monitor bird health, track vaccinations, and manage veterinary records with ease.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <div className="bg-primary/10 rounded-full p-3 w-fit mx-auto mb-4">
                <Users className="h-8 w-8 text-primary" />
              </div>
              <CardTitle>Flock Management</CardTitle>
              <CardDescription>
                Organize your birds by breed, age, and location with comprehensive flock management tools.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-white rounded-lg p-8 shadow-sm">
          <h2 className="text-3xl font-bold text-balance mb-4">Ready to Transform Your Farm?</h2>
          <p className="text-muted-foreground text-pretty mb-6 max-w-xl mx-auto">
            Join thousands of farmers who trust PoultryPro to manage their operations efficiently.
          </p>
          <Button size="lg" asChild>
            <Link href="/register">Get Started Today</Link>
          </Button>
        </div>
      </main>
    </div>
  )
}
