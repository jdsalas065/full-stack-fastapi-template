import { Filter, Plus, Search } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"

export interface FilterField {
  name: string
  label: string
  type: "text" | "number" | "date" | "datetime" | "select"
  placeholder?: string
  options?: { label: string; value: string }[]
}

export interface FilterBarConfig {
  showTotalItems?: boolean
  showItemsPerPage?: boolean
  showSearchBox?: boolean
  showFilterButton?: boolean
  showCreateButton?: boolean
  searchPlaceholder?: string
  createButtonLabel?: string
  advancedFilters?: FilterField[]
}

interface FilterBarProps {
  config?: FilterBarConfig
  totalItems?: number
  itemsPerPage?: number
  searchValue?: string
  onSearchChange?: (value: string) => void
  onCreateClick?: () => void
  onFilterApply?: (filters: Record<string, any>) => void
  className?: string
}

export function FilterBar({
  config = {},
  totalItems = 0,
  itemsPerPage = 10,
  searchValue = "",
  onSearchChange,
  onCreateClick,
  onFilterApply,
  className = "",
}: FilterBarProps) {
  const {
    showTotalItems = true,
    showItemsPerPage = true,
    showSearchBox = true,
    showFilterButton = true,
    showCreateButton = true,
    searchPlaceholder = "Search...",
    createButtonLabel = "Create New",
    advancedFilters = [],
  } = config

  const [filterValues, setFilterValues] = useState<Record<string, any>>({})
  const [isFilterOpen, setIsFilterOpen] = useState(false)

  const handleFilterChange = (name: string, value: any) => {
    setFilterValues((prev) => ({ ...prev, [name]: value }))
  }

  const handleApplyFilters = () => {
    if (onFilterApply) {
      onFilterApply(filterValues)
    }
    setIsFilterOpen(false)
  }

  const handleResetFilters = () => {
    setFilterValues({})
    if (onFilterApply) {
      onFilterApply({})
    }
  }

  return (
    <div className={`flex flex-col gap-4 ${className}`}>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          {showTotalItems && (
            <div className="flex items-center gap-2">
              <span className="font-medium text-foreground">{totalItems}</span>
              <span>total items</span>
            </div>
          )}
          {showItemsPerPage && (
            <div className="flex items-center gap-2">
              <span className="font-medium text-foreground">
                {itemsPerPage}
              </span>
              <span>per page</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          {showSearchBox && (
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="text"
                placeholder={searchPlaceholder}
                value={searchValue}
                onChange={(e) => onSearchChange?.(e.target.value)}
                className="pl-9"
              />
            </div>
          )}

          {showFilterButton && advancedFilters.length > 0 && (
            <Sheet open={isFilterOpen} onOpenChange={setIsFilterOpen}>
              <SheetTrigger asChild>
                <Button variant="outline" size="icon">
                  <Filter className="h-4 w-4" />
                </Button>
              </SheetTrigger>
              <SheetContent>
                <SheetHeader>
                  <SheetTitle>Advanced Filters</SheetTitle>
                  <SheetDescription>
                    Apply filters to refine your search
                  </SheetDescription>
                </SheetHeader>
                <div className="flex flex-col gap-4 py-4">
                  {advancedFilters.map((field) => (
                    <div key={field.name} className="flex flex-col gap-2">
                      <label
                        htmlFor={field.name}
                        className="text-sm font-medium"
                      >
                        {field.label}
                      </label>
                      {field.type === "select" ? (
                        <select
                          id={field.name}
                          value={filterValues[field.name] || ""}
                          onChange={(e) =>
                            handleFilterChange(field.name, e.target.value)
                          }
                          className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors"
                        >
                          <option value="">Select...</option>
                          {field.options?.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <Input
                          id={field.name}
                          type={field.type}
                          placeholder={field.placeholder}
                          value={filterValues[field.name] || ""}
                          onChange={(e) =>
                            handleFilterChange(field.name, e.target.value)
                          }
                        />
                      )}
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleApplyFilters} className="flex-1">
                    Apply Filters
                  </Button>
                  <Button
                    onClick={handleResetFilters}
                    variant="outline"
                    className="flex-1"
                  >
                    Reset
                  </Button>
                </div>
              </SheetContent>
            </Sheet>
          )}

          {showCreateButton && (
            <Button onClick={onCreateClick}>
              <Plus className="h-4 w-4 mr-2" />
              {createButtonLabel}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
