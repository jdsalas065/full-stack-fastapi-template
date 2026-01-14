import { createFileRoute, Link, Outlet, redirect } from "@tanstack/react-router"
import type { LucideIcon } from "lucide-react"

import { Footer } from "@/components/Common/Footer"
import { UserMenu } from "@/components/Common/UserMenu"
import { Button } from "@/components/ui/button"
import { isLoggedIn } from "@/hooks/useAuth"
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
  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Header with Navigation Buttons */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <div className="text-2xl font-bold text-primary">Portal Demo</div>
            <div className="flex items-center gap-2">
              {navigationItems.map((item) => {
                return (
                  <Button key={item.to} asChild variant="ghost">
                    <Link to={item.to}>{item.label}</Link>
                  </Button>
                )
              })}
            </div>
          </div>
          <UserMenu />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="container mx-auto py-8 px-4 space-y-8 w-full max-w-full">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}

export default Layout
