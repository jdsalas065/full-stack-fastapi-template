import { createFileRoute, Outlet } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/table2")({
  component: Table2Layout,
})

function Table2Layout() {
  return <Outlet />
}
