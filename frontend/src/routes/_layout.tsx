import { createFileRoute, Link, Outlet, redirect } from "@tanstack/react-router"
import { Briefcase, Home, type LucideIcon, Settings, Users } from "lucide-react"

import { Footer } from "@/components/Common/Footer"
import { Button } from "@/components/ui/button"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import type { FileRoutesByTo } from "@/routeTree.gen"

interface NavItem {
  to: keyof FileRoutesByTo
  label: string
  icon?: LucideIcon
  requiresSuperuser?: boolean
}

const navigationItems: NavItem[] = [
  { to: "/demo", label: "Demo" },
  { to: "/table1", label: "Table 1" },
  { to: "/table2", label: "Table 2" },
  { to: "/table3", label: "Table 3" },
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/items", label: "Items", icon: Briefcase },
  { to: "/admin", label: "Admin", icon: Users, requiresSuperuser: true },
  { to: "/settings", label: "Settings", icon: Settings },
]

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
              {navigationItems.map((item) => {
                // Skip admin link if user is not superuser
                if (item.requiresSuperuser && !currentUser?.is_superuser) {
                  return null
                }

                const Icon = item.icon

                return (
                  <Button key={item.to} asChild variant="ghost">
                    <Link to={item.to}>
                      {Icon && <Icon className="h-4 w-4 mr-2" />}
                      {item.label}
                    </Link>
                  </Button>
                )
              })}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="container py-8 px-4 space-y-8">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}

export default Layout
