import { createFileRoute, Outlet } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/table1")({
  component: Table1Layout,
})

function Table1Layout() {
  return <Outlet />
}
