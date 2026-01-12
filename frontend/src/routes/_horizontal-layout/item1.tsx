import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { EnhancedDataTable } from "@/components/Common/EnhancedDataTable"
import { FilterBar } from "@/components/Common/FilterBar"
import { MediaViewer } from "@/components/Common/MediaViewer"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { sampleColumns } from "@/data/sampleColumns"
import { sampleData } from "@/data/sampleData"

export const Route = createFileRoute("/_horizontal-layout/item1")({
  component: Item1Page,
  head: () => ({
    meta: [
      {
        title: "Item 1 - Portal Dashboard",
      },
    ],
  }),
})

function Item1Page() {
  const [searchValue, setSearchValue] = useState("")
  const [filteredData, setFilteredData] = useState(sampleData)

  const handleSearch = (value: string) => {
    setSearchValue(value)
    if (value.trim() === "") {
      setFilteredData(sampleData)
    } else {
      const filtered = sampleData.filter(
        (item) =>
          item.name.toLowerCase().includes(value.toLowerCase()) ||
          item.email.toLowerCase().includes(value.toLowerCase()) ||
          item.role.toLowerCase().includes(value.toLowerCase())
      )
      setFilteredData(filtered)
    }
  }

  const handleFilterApply = (filters: Record<string, any>) => {
    let filtered = sampleData

    if (filters.status) {
      filtered = filtered.filter((item) => item.status === filters.status)
    }
    if (filters.department) {
      filtered = filtered.filter(
        (item) => item.department === filters.department
      )
    }
    if (filters.location) {
      filtered = filtered.filter((item) =>
        item.location.toLowerCase().includes(filters.location.toLowerCase())
      )
    }

    // Apply search if active
    if (searchValue.trim() !== "") {
      filtered = filtered.filter(
        (item) =>
          item.name.toLowerCase().includes(searchValue.toLowerCase()) ||
          item.email.toLowerCase().includes(searchValue.toLowerCase()) ||
          item.role.toLowerCase().includes(searchValue.toLowerCase())
      )
    }

    setFilteredData(filtered)
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Item 1 - Users Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage and view all users in your organization
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>User Directory</CardTitle>
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
                    { label: "Product", value: "Product" },
                    { label: "Design", value: "Design" },
                    { label: "Marketing", value: "Marketing" },
                    { label: "Sales", value: "Sales" },
                    { label: "Human Resources", value: "Human Resources" },
                    { label: "Analytics", value: "Analytics" },
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
            pageSize={10}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Media Gallery Sample</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <MediaViewer
              src="https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=400"
              alt="Sample User Photo"
              type="image"
            />
            <MediaViewer
              src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400"
              alt="Team Member"
              type="image"
            />
            <MediaViewer
              src="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
              alt="Sample Document"
              type="pdf"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
