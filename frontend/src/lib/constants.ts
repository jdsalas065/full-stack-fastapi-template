export const statusVariants = {
  active: "bg-success/10 text-success border-success/20",
  inactive: "bg-muted text-muted-foreground border-border",
  pending: "bg-primary/10 text-primary border-primary/20",
} as const

export type Status = keyof typeof statusVariants
