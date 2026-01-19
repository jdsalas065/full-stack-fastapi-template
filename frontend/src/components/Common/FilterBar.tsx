import { Filter, Plus, Search, Trash2 } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

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
  showDeleteButton?: boolean
  searchPlaceholder?: string
  createButtonLabel?: string
  advancedFilters?: FilterField[]
  itemsPerPageOptions?: number[]
}

interface FilterBarProps {
  config?: FilterBarConfig
  totalItems?: number
  itemsPerPage?: number
  searchValue?: string
  selectedCount?: number
  onSearchChange?: (value: string) => void
  onCreateClick?: () => void
  onDeleteClick?: () => void
  onFilterApply?: (filters: Record<string, any>) => void
  onItemsPerPageChange?: (value: number) => void
  className?: string
}

export function FilterBar({
  config = {},
  totalItems = 0,
  itemsPerPage = 10,
  searchValue = "",
  selectedCount = 0,
  onSearchChange,
  onCreateClick,
  onDeleteClick,
  onFilterApply,
  onItemsPerPageChange,
  className = "",
}: FilterBarProps) {
  const {
    showTotalItems = true,
    showItemsPerPage = true,
    showSearchBox = true,
    showFilterButton = true,
    showCreateButton = true,
    showDeleteButton = false,
    searchPlaceholder = "Search...",
    createButtonLabel = "Create New",
    advancedFilters = [],
    itemsPerPageOptions = [10, 20, 30, 100],
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
          {selectedCount > 0 ? (
            <>
              {showDeleteButton && onDeleteClick && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={onDeleteClick}
                  className="gap-2"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete ({selectedCount})
                </Button>
              )}
              {showItemsPerPage && onItemsPerPageChange && (
                <div className="flex items-center gap-2">
                  <span>Items per page:</span>
                  <Select
                    value={`${itemsPerPage}`}
                    onValueChange={(value) =>
                      onItemsPerPageChange(Number(value))
                    }
                  >
                    <SelectTrigger className="h-8 w-[70px]">
                      <SelectValue placeholder={itemsPerPage} />
                    </SelectTrigger>
                    <SelectContent side="bottom">
                      {itemsPerPageOptions.map((option) => (
                        <SelectItem key={option} value={`${option}`}>
                          {option}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </>
          ) : (
            <>
              {showTotalItems && (
                <div className="flex items-center gap-2">
                  <span className="font-medium text-foreground">
                    {totalItems}
                  </span>
                  <span>total items</span>
                </div>
              )}
              {showItemsPerPage && onItemsPerPageChange && (
                <div className="flex items-center gap-2">
                  <span>Items per page:</span>
                  <Select
                    value={`${itemsPerPage}`}
                    onValueChange={(value) =>
                      onItemsPerPageChange(Number(value))
                    }
                  >
                    <SelectTrigger className="h-8 w-[70px]">
                      <SelectValue placeholder={itemsPerPage} />
                    </SelectTrigger>
                    <SelectContent side="bottom">
                      {itemsPerPageOptions.map((option) => (
                        <SelectItem key={option} value={`${option}`}>
                          {option}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </>
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
            <Popover open={isFilterOpen} onOpenChange={setIsFilterOpen}>
              <PopoverTrigger asChild>
                <Button variant="outline" size="icon">
                  <Filter className="h-4 w-4" />
                </Button>
              </PopoverTrigger>
              <PopoverContent align="end" className="w-80">
                <div className="flex flex-col gap-4">
                  <div className="space-y-2">
                    <h4 className="font-medium leading-none">
                      Advanced Filters
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Apply filters to refine your search
                    </p>
                  </div>
                  <div className="flex flex-col gap-4">
                    {advancedFilters.map((field) => (
                      <div key={field.name} className="flex flex-col gap-2">
                        <label
                          htmlFor={field.name}
                          className="text-sm font-medium"
                        >
                          {field.label}
                        </label>
                        {field.type === "select" ? (
                          <Select
                            value={filterValues[field.name] || ""}
                            onValueChange={(value) =>
                              handleFilterChange(field.name, value)
                            }
                          >
                            <SelectTrigger id={field.name}>
                              <SelectValue placeholder="Select..." />
                            </SelectTrigger>
                            <SelectContent>
                              {field.options?.map((option) => (
                                <SelectItem
                                  key={option.value}
                                  value={option.value}
                                >
                                  {option.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
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
                </div>
              </PopoverContent>
            </Popover>
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
