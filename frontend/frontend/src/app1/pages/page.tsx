import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/auth-context"
import { Card, CardContent } from "../components/ui/card"
import { Bird } from "lucide-react"

export default function HomePage() {
  const { isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        navigate("/dashboard")
      } else {
        navigate("/login")
      }
    }
  }, [isAuthenticated, loading, navigate])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="w-96">
          <CardContent className="flex flex-col items-center justify-center p-8">
            <Bird className="h-12 w-12 text-primary animate-pulse mb-4" />
            <h1 className="text-2xl font-semibold text-center mb-2">PoultryPro</h1>
            <p className="text-muted-foreground text-center">Loading...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return null
}
