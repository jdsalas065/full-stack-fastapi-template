import { Link as RouterLink, useRouterState } from "@tanstack/react-router"
import type { LucideIcon } from "lucide-react"

import { cn } from "@/lib/utils"

export type NavItem = {
  icon?: LucideIcon
  title: string
  path: string
}

interface HorizontalNavProps {
  items: NavItem[]
  className?: string
}

export function HorizontalNav({ items, className }: HorizontalNavProps) {
  const router = useRouterState()
  const currentPath = router.location.pathname

  return (
    <nav
      className={cn(
        "flex items-center gap-1 border-b bg-background px-4",
        className
      )}
    >
      {items.map((item) => {
        const isActive = currentPath === item.path

        return (
          <RouterLink
            key={item.path}
            to={item.path}
            className={cn(
              "flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px",
              isActive
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
            )}
          >
            {item.icon && <item.icon className="h-4 w-4" />}
            <span>{item.title}</span>
          </RouterLink>
        )
      })}
    </nav>
  )
}
