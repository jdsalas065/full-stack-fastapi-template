import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import { Briefcase, Home, Users } from "lucide-react"
import { SidebarAppearance } from "@/components/Common/Appearance"
import { Footer } from "@/components/Common/Footer"
import { HorizontalNav } from "@/components/Common/HorizontalNav"
import { Logo } from "@/components/Common/Logo"
import { User } from "@/components/Sidebar/User"
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

  const navItems = [
    { icon: Home, title: "Dashboard", path: "/" },
    { icon: Briefcase, title: "Items", path: "/items" },
  ]

  // Add admin menu item if user is superuser
  if (currentUser?.is_superuser) {
    navItems.push({ icon: Users, title: "Admin", path: "/admin" })
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <Logo variant="responsive" />
          </div>
          <div className="flex items-center gap-2">
            <SidebarAppearance />
            <User user={currentUser} />
          </div>
        </div>
        <HorizontalNav items={navItems} />
      </header>
      <main className="flex-1">
        <div className="container mx-auto py-6 px-4 md:px-8">
          <Outlet />
        </div>
      </main>
      <Footer />
    </div>
  )
}

export default Layout
