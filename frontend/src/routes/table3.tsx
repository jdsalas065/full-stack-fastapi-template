import { createFileRoute, Link } from "@tanstack/react-router"
import { useState } from "react"
import { EnhancedDataTable } from "@/components/Common/EnhancedDataTable"
import { FilterBar } from "@/components/Common/FilterBar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { sampleColumns } from "@/data/sampleColumns"
import { tableData3 } from "@/data/tableData3"

export const Route = createFileRoute("/table3")({
  component: Table3Page,
  head: () => ({
    meta: [
      {
        title: "Table 3 - Portal",
      },
    ],
  }),
})

function Table3Page() {
  const [searchValue, setSearchValue] = useState("")
  const [filteredData, setFilteredData] = useState(tableData3)

  const handleSearch = (value: string) => {
    setSearchValue(value)
    if (value.trim() === "") {
      setFilteredData(tableData3)
    } else {
      const filtered = tableData3.filter(
        (item) =>
          item.name.toLowerCase().includes(value.toLowerCase()) ||
          item.email.toLowerCase().includes(value.toLowerCase()) ||
          item.role.toLowerCase().includes(value.toLowerCase()),
      )
      setFilteredData(filtered)
    }
  }

  const handleFilterApply = (filters: Record<string, any>) => {
    let filtered = tableData3

    if (filters.status) {
      filtered = filtered.filter((item) => item.status === filters.status)
    }
    if (filters.department) {
      filtered = filtered.filter(
        (item) => item.department === filters.department,
      )
    }
    if (filters.location) {
      filtered = filtered.filter((item) =>
        item.location.toLowerCase().includes(filters.location.toLowerCase()),
      )
    }

    if (searchValue.trim() !== "") {
      filtered = filtered.filter(
        (item) =>
          item.name.toLowerCase().includes(searchValue.toLowerCase()) ||
          item.email.toLowerCase().includes(searchValue.toLowerCase()) ||
          item.role.toLowerCase().includes(searchValue.toLowerCase()),
      )
    }

    setFilteredData(filtered)
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Header with Navigation Buttons */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <div className="text-2xl font-bold text-primary">Portal Demo</div>
            <div className="flex items-center gap-2">
              <Button asChild variant="ghost">
                <Link to="/table1">Table 1</Link>
              </Button>
              <Button asChild variant="ghost">
                <Link to="/table2">Table 2</Link>
              </Button>
              <Button asChild variant="ghost">
                <Link to="/table3">Table 3</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="container py-8 px-4 space-y-8">
          {/* Page Header */}
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Table 3 - Sales & Support</h1>
            <p className="text-muted-foreground mt-2 text-lg">
              View and manage sales and support team members
            </p>
          </div>

          {/* Filter Bar & Data Table */}
          <Card>
            <CardHeader>
              <CardTitle>Sales & Support Team Data</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FilterBar
                config={{
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
                      type: "select",
                      options: [
                        { label: "Active", value: "active" },
                        { label: "Inactive", value: "inactive" },
                        { label: "Pending", value: "pending" },
                      ],
                    },
                    {
                      name: "department",
                      label: "Department",
                      type: "select",
                      options: [
                        { label: "Engineering", value: "Engineering" },
                        { label: "Sales", value: "Sales" },
                        { label: "Marketing", value: "Marketing" },
                      ],
                    },
                    {
                      name: "location",
                      label: "Location",
                      type: "text",
                      placeholder: "Enter location...",
                    },
                  ],
                }}
                totalItems={filteredData.length}
                itemsPerPage={10}
                searchValue={searchValue}
                onSearchChange={handleSearch}
                onCreateClick={() => alert("Create new user clicked!")}
                onFilterApply={handleFilterApply}
              />

              <EnhancedDataTable
                columns={sampleColumns}
                data={filteredData}
                enableSorting={true}
                enablePagination={true}
                pageSize={5}
              />
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t py-6">
        <div className="container px-4 text-center text-sm text-muted-foreground">
          <p>Portal Frontend Base - 2026</p>
        </div>
      </footer>
    </div>
  )
}
