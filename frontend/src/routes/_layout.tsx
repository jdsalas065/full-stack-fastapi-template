import { createFileRoute, Link, Outlet, redirect } from "@tanstack/react-router"
import { Briefcase, Home, Settings, Users } from "lucide-react"

import { Footer } from "@/components/Common/Footer"
import { Button } from "@/components/ui/button"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  const { user: currentUser } = useAuth()

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Header with Navigation Buttons */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <div className="text-2xl font-bold text-primary">Portal Demo</div>
            <div className="flex items-center gap-2">
              <Button asChild variant="ghost">
                <Link to="/">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </Link>
              </Button>
              <Button asChild variant="ghost">
                <Link to="/items">
                  <Briefcase className="h-4 w-4 mr-2" />
                  Items
                </Link>
              </Button>
              {currentUser?.is_superuser && (
                <Button asChild variant="ghost">
                  <Link to="/admin">
                    <Users className="h-4 w-4 mr-2" />
                    Admin
                  </Link>
                </Button>
              )}
              <Button asChild variant="ghost">
                <Link to="/settings">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="container py-8 px-4">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}

export default Layout
