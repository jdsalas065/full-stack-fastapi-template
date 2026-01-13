import { useMemo, useState } from "react"

interface FilterConfig {
  status?: string
  department?: string
  location?: string
}

interface TableItem {
  name: string
  email: string
  role: string
  status: string
  department: string
  location: string
  [key: string]: any
}

export function useTableFilter<T extends TableItem>(data: T[]) {
  const [searchValue, setSearchValue] = useState("")
  const [filters, setFilters] = useState<FilterConfig>({})

  const filteredData = useMemo(() => {
    let result = [...data]

    // Apply status filter
    if (filters.status) {
      result = result.filter((item) => item.status === filters.status)
    }

    // Apply department filter
    if (filters.department) {
      result = result.filter((item) => item.department === filters.department)
    }

    // Apply location filter
    if (filters.location) {
      result = result.filter((item) =>
        item.location.toLowerCase().includes(filters.location?.toLowerCase() || ''),
      )
    }

    // Apply search filter
    if (searchValue.trim() !== "") {
      const searchLower = searchValue.toLowerCase()
      result = result.filter(
        (item) =>
          item.name.toLowerCase().includes(searchLower) ||
          item.email.toLowerCase().includes(searchLower) ||
          item.role.toLowerCase().includes(searchLower),
      )
    }

    return result
  }, [data, filters, searchValue])

  const handleSearch = (value: string) => {
    setSearchValue(value)
  }

  const handleFilterApply = (newFilters: FilterConfig) => {
    setFilters(newFilters)
  }

  const clearFilters = () => {
    setSearchValue("")
    setFilters({})
  }

  return {
    filteredData,
    searchValue,
    filters,
    handleSearch,
    handleFilterApply,
    clearFilters,
  }
}
