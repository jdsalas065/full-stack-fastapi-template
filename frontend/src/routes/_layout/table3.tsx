import { createFileRoute, Outlet } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/table3")({
  component: Table3Layout,
})

function Table3Layout() {
  return <Outlet />
}
