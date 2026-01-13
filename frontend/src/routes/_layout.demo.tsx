import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { EnhancedDataTable } from "@/components/Common/EnhancedDataTable"
import { FilterBar } from "@/components/Common/FilterBar"
import { MediaViewer } from "@/components/Common/MediaViewer"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { sampleColumns } from "@/data/sampleColumns"
import { sampleData } from "@/data/sampleData"

export const Route = createFileRoute("/_layout/demo")({
  component: DemoPage,
  head: () => ({
    meta: [
      {
        title: "Component Demo - Portal",
      },
    ],
  }),
})

function DemoPage() {
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
          item.role.toLowerCase().includes(value.toLowerCase()),
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
    <>
      <div>
        <h1 className="text-4xl font-bold tracking-tight">
          Frontend Component Demo
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">
          Showcasing the new horizontal navigation, enhanced data table,
          filter bar, and media viewer components
        </p>
      </div>

          {/* Color Palette Demo */}
          <Card>
            <CardHeader>
              <CardTitle>New Color System</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <div className="h-24 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-semibold">
                    Primary (#7F56D9)
                  </div>
                  <p className="text-sm text-muted-foreground text-center">
                    Used for main actions and emphasis
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="h-24 rounded-lg bg-destructive flex items-center justify-center text-white font-semibold">
                    Error (#D92D20)
                  </div>
                  <p className="text-sm text-muted-foreground text-center">
                    Used for errors and warnings
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="h-24 rounded-lg bg-success flex items-center justify-center text-success-foreground font-semibold">
                    Success (#039855)
                  </div>
                  <p className="text-sm text-muted-foreground text-center">
                    Used for success states
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Filter Bar & Data Table Demo */}
          <Card>
            <CardHeader>
              <CardTitle>Enhanced Data Table with Filter Bar</CardTitle>
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
                pageSize={5}
              />
            </CardContent>
          </Card>

          {/* Media Viewer Demo */}
          <Card>
            <CardHeader>
              <CardTitle>Media Viewer Component</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Click on any thumbnail to view in full screen with zoom controls
              </p>
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
                  src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
                  alt="Profile Picture"
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

          {/* Features List */}
          <Card>
            <CardHeader>
              <CardTitle>Key Features</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-2 text-primary">
                    ✓ Horizontal Navigation
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Tab-based navigation with active state indicators and
                    responsive design
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2 text-primary">
                    ✓ Enhanced Filter Bar
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Configurable filters with search, advanced filters, and
                    action buttons
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2 text-primary">
                    ✓ Dynamic Data Table
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Sorting, pagination, filtering with customizable columns and
                    actions
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2 text-primary">
                    ✓ Media Viewer
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Preview and view images and PDFs with zoom and download
                    controls
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2 text-primary">
                    ✓ New Color Theme
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Purple primary, red error, green success - optimized for
                    light and dark modes
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2 text-primary">
                    ✓ Fully Configurable
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    All components accept config objects for maximum flexibility
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
    </>
  )
}
