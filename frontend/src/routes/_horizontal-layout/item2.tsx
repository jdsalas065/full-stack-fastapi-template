import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { EnhancedDataTable } from "@/components/Common/EnhancedDataTable"
import { FilterBar } from "@/components/Common/FilterBar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { ColumnDef } from "@tanstack/react-table"

interface ProjectData {
  id: string
  name: string
  status: "in-progress" | "completed" | "on-hold"
  priority: "high" | "medium" | "low"
  budget: number
  startDate: string
  endDate: string
  team: string
}

const projectData: ProjectData[] = [
  {
    id: "1",
    name: "E-commerce Platform",
    status: "in-progress",
    priority: "high",
    budget: 150000,
    startDate: "2024-01-01",
    endDate: "2024-06-30",
    team: "Team Alpha",
  },
  {
    id: "2",
    name: "Mobile App Development",
    status: "in-progress",
    priority: "high",
    budget: 200000,
    startDate: "2024-02-15",
    endDate: "2024-08-15",
    team: "Team Beta",
  },
  {
    id: "3",
    name: "Data Analytics Dashboard",
    status: "completed",
    priority: "medium",
    budget: 80000,
    startDate: "2023-10-01",
    endDate: "2024-01-31",
    team: "Team Gamma",
  },
  {
    id: "4",
    name: "CRM System Integration",
    status: "on-hold",
    priority: "low",
    budget: 50000,
    startDate: "2024-03-01",
    endDate: "2024-05-31",
    team: "Team Delta",
  },
  {
    id: "5",
    name: "AI Chatbot Implementation",
    status: "in-progress",
    priority: "high",
    budget: 120000,
    startDate: "2024-01-15",
    endDate: "2024-07-15",
    team: "Team Epsilon",
  },
  {
    id: "6",
    name: "Cloud Migration",
    status: "completed",
    priority: "high",
    budget: 300000,
    startDate: "2023-08-01",
    endDate: "2023-12-31",
    team: "Team Zeta",
  },
]

const projectColumns: ColumnDef<ProjectData>[] = [
  {
    accessorKey: "name",
    header: "Project Name",
    cell: ({ row }) => (
      <span className="font-medium">{row.original.name}</span>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status
      const statusColors = {
        "in-progress": "bg-primary/10 text-primary border-primary/20",
        completed: "bg-success/10 text-success border-success/20",
        "on-hold": "bg-muted text-muted-foreground border-border",
      }
      return (
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusColors[status]}`}
        >
          {status.replace("-", " ").toUpperCase()}
        </span>
      )
    },
  },
  {
    accessorKey: "priority",
    header: "Priority",
    cell: ({ row }) => {
      const priority = row.original.priority
      const priorityColors = {
        high: "text-destructive",
        medium: "text-primary",
        low: "text-muted-foreground",
      }
      return (
        <span className={`font-medium ${priorityColors[priority]}`}>
          {priority.charAt(0).toUpperCase() + priority.slice(1)}
        </span>
      )
    },
  },
  {
    accessorKey: "budget",
    header: "Budget",
    cell: ({ row }) => {
      const amount = row.original.budget
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount)
    },
  },
  {
    accessorKey: "team",
    header: "Team",
  },
  {
    accessorKey: "startDate",
    header: "Start Date",
    cell: ({ row }) => {
      const date = new Date(row.original.startDate)
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    },
  },
  {
    accessorKey: "endDate",
    header: "End Date",
    cell: ({ row }) => {
      const date = new Date(row.original.endDate)
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    },
  },
]

export const Route = createFileRoute("/_horizontal-layout/item2")({
  component: Item2Page,
  head: () => ({
    meta: [
      {
        title: "Item 2 - Portal Dashboard",
      },
    ],
  }),
})

function Item2Page() {
  const [searchValue, setSearchValue] = useState("")
  const [filteredData, setFilteredData] = useState(projectData)

  const handleSearch = (value: string) => {
    setSearchValue(value)
    if (value.trim() === "") {
      setFilteredData(projectData)
    } else {
      const filtered = projectData.filter(
        (item) =>
          item.name.toLowerCase().includes(value.toLowerCase()) ||
          item.team.toLowerCase().includes(value.toLowerCase())
      )
      setFilteredData(filtered)
    }
  }

  const handleFilterApply = (filters: Record<string, any>) => {
    let filtered = projectData

    if (filters.status) {
      filtered = filtered.filter((item) => item.status === filters.status)
    }
    if (filters.priority) {
      filtered = filtered.filter((item) => item.priority === filters.priority)
    }

    if (searchValue.trim() !== "") {
      filtered = filtered.filter(
        (item) =>
          item.name.toLowerCase().includes(searchValue.toLowerCase()) ||
          item.team.toLowerCase().includes(searchValue.toLowerCase())
      )
    }

    setFilteredData(filtered)
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Item 2 - Projects Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Track and manage all ongoing projects
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Project Portfolio</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <FilterBar
            config={{
              showTotalItems: true,
              showItemsPerPage: true,
              showSearchBox: true,
              showFilterButton: true,
              showCreateButton: true,
              searchPlaceholder: "Search projects...",
              createButtonLabel: "New Project",
              advancedFilters: [
                {
                  name: "status",
                  label: "Status",
                  type: "select",
                  options: [
                    { label: "In Progress", value: "in-progress" },
                    { label: "Completed", value: "completed" },
                    { label: "On Hold", value: "on-hold" },
                  ],
                },
                {
                  name: "priority",
                  label: "Priority",
                  type: "select",
                  options: [
                    { label: "High", value: "high" },
                    { label: "Medium", value: "medium" },
                    { label: "Low", value: "low" },
                  ],
                },
                {
                  name: "startDate",
                  label: "Start Date",
                  type: "date",
                },
                {
                  name: "endDate",
                  label: "End Date",
                  type: "date",
                },
              ],
            }}
            totalItems={filteredData.length}
            itemsPerPage={10}
            searchValue={searchValue}
            onSearchChange={handleSearch}
            onCreateClick={() => alert("Create new project clicked!")}
            onFilterApply={handleFilterApply}
          />

          <EnhancedDataTable
            columns={projectColumns}
            data={filteredData}
            enableSorting={true}
            enablePagination={true}
            pageSize={10}
          />
        </CardContent>
      </Card>
    </div>
  )
}
