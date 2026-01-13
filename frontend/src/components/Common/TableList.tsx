import { EnhancedDataTable } from "@/components/Common/EnhancedDataTable"
import { FilterBar } from "@/components/Common/FilterBar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { sampleColumns } from "@/data/sampleColumns"
import { useTableFilter } from "@/hooks/useTableFilter"

interface TableListProps<T> {
  title: string
  description: string
  data: T[]
  navigateToDetail: (id: string) => void
  filterConfig?: {
    statusOptions?: { label: string; value: string }[]
    departmentOptions?: { label: string; value: string }[]
  }
}

export function TableList<
  T extends {
    id: string
    name: string
    email: string
    role: string
    status: string
    department: string
    location: string
    [key: string]: any
  },
>({
  title,
  description,
  data,
  navigateToDetail,
  filterConfig,
}: TableListProps<T>) {
  const { filteredData, searchValue, handleSearch, handleFilterApply } =
    useTableFilter(data as any)

  const handleRowClick = (row: any) => {
    navigateToDetail(row.id)
  }

  const defaultFilterConfig = {
    showTotalItems: true,
    showItemsPerPage: true,
    showSearchBox: true,
    showFilterButton: true,
    showCreateButton: true,
    searchPlaceholder: "Search users...",
    createButtonLabel: "Add User",
    advancedFilters: [
      {
        name: "status",
        label: "Status",
        type: "select" as const,
        options: filterConfig?.statusOptions || [
          { label: "Active", value: "active" },
          { label: "Inactive", value: "inactive" },
          { label: "Pending", value: "pending" },
        ],
      },
      {
        name: "department",
        label: "Department",
        type: "select" as const,
        options: filterConfig?.departmentOptions || [
          { label: "Engineering", value: "Engineering" },
          { label: "Product", value: "Product" },
          { label: "Design", value: "Design" },
        ],
      },
      {
        name: "location",
        label: "Location",
        type: "text" as const,
        placeholder: "Enter location...",
      },
    ],
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight">{title}</h1>
        <p className="text-muted-foreground mt-2 text-lg">{description}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{title} Data</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <FilterBar
            config={defaultFilterConfig}
            totalItems={filteredData.length}
            itemsPerPage={10}
            searchValue={searchValue}
            onSearchChange={handleSearch}
            onCreateClick={() => alert("Create new user clicked!")}
            onFilterApply={handleFilterApply}
          />

          <EnhancedDataTable
            columns={sampleColumns}
            data={filteredData as any}
            enableSorting={true}
            enablePagination={true}
            pageSize={5}
            onRowClick={handleRowClick}
          />
        </CardContent>
      </Card>
    </div>
  )
}
