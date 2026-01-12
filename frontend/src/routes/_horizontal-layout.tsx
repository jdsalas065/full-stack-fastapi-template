import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import { FileText, Home, Layout } from "lucide-react"

import { Footer } from "@/components/Common/Footer"
import { HorizontalNav } from "@/components/Common/HorizontalNav"
import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import { User } from "@/components/Sidebar/User"
import { isLoggedIn } from "@/hooks/useAuth"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_horizontal-layout")({
  component: HorizontalLayout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

const navItems = [
  { icon: Home, title: "Item 1", path: "/item1" },
  { icon: Layout, title: "Item 2", path: "/item2" },
  { icon: FileText, title: "Item 3", path: "/item3" },
]

function HorizontalLayout() {
  const { user: currentUser } = useAuth()

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
        <div className="container py-6 px-4 md:px-8">
          <Outlet />
        </div>
      </main>
      <Footer />
    </div>
  )
}

export default HorizontalLayout
