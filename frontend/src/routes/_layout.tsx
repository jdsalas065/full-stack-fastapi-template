import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

import { SharedLayout } from "@/components/Common/SharedLayout"
import { isLoggedIn } from "@/hooks/useAuth"

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
    <SharedLayout>
      <Outlet />
    </SharedLayout>
  )
}

export default Layout
