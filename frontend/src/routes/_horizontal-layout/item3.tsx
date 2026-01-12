import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { EnhancedDataTable } from "@/components/Common/EnhancedDataTable"
import { FilterBar } from "@/components/Common/FilterBar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { ColumnDef } from "@tanstack/react-table"

interface TaskData {
  id: string
  title: string
  assignee: string
  status: "todo" | "in-progress" | "review" | "completed"
  priority: "high" | "medium" | "low"
  dueDate: string
  estimatedHours: number
  completedHours: number
}

const taskData: TaskData[] = [
  {
    id: "1",
    title: "Design homepage mockup",
    assignee: "Sarah Wilson",
    status: "completed",
    priority: "high",
    dueDate: "2024-01-15",
    estimatedHours: 8,
    completedHours: 7,
  },
  {
    id: "2",
    title: "Implement user authentication",
    assignee: "John Doe",
    status: "in-progress",
    priority: "high",
    dueDate: "2024-01-20",
    estimatedHours: 16,
    completedHours: 10,
  },
  {
    id: "3",
    title: "Write API documentation",
    assignee: "Jennifer White",
    status: "review",
    priority: "medium",
    dueDate: "2024-01-18",
    estimatedHours: 12,
    completedHours: 12,
  },
  {
    id: "4",
    title: "Fix mobile responsiveness",
    assignee: "Christopher Lee",
    status: "in-progress",
    priority: "high",
    dueDate: "2024-01-17",
    estimatedHours: 6,
    completedHours: 4,
  },
  {
    id: "5",
    title: "Optimize database queries",
    assignee: "David Martinez",
    status: "todo",
    priority: "medium",
    dueDate: "2024-01-25",
    estimatedHours: 10,
    completedHours: 0,
  },
  {
    id: "6",
    title: "Update security dependencies",
    assignee: "Emily Davis",
    status: "in-progress",
    priority: "high",
    dueDate: "2024-01-16",
    estimatedHours: 4,
    completedHours: 3,
  },
  {
    id: "7",
    title: "Create user onboarding flow",
    assignee: "Jane Smith",
    status: "review",
    priority: "medium",
    dueDate: "2024-01-22",
    estimatedHours: 14,
    completedHours: 14,
  },
  {
    id: "8",
    title: "Implement notification system",
    assignee: "Michael Johnson",
    status: "todo",
    priority: "low",
    dueDate: "2024-01-30",
    estimatedHours: 20,
    completedHours: 0,
  },
]

const taskColumns: ColumnDef<TaskData>[] = [
  {
    accessorKey: "title",
    header: "Task",
    cell: ({ row }) => (
      <span className="font-medium">{row.original.title}</span>
    ),
  },
  {
    accessorKey: "assignee",
    header: "Assignee",
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status
      const statusColors = {
        todo: "bg-muted text-muted-foreground border-border",
        "in-progress": "bg-primary/10 text-primary border-primary/20",
        review: "bg-primary/20 text-primary border-primary/30",
        completed: "bg-success/10 text-success border-success/20",
      }
      return (
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusColors[status]}`}
        >
          {status
            .split("-")
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ")}
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
    accessorKey: "dueDate",
    header: "Due Date",
    cell: ({ row }) => {
      const date = new Date(row.original.dueDate)
      const today = new Date()
      const isOverdue = date < today && row.original.status !== "completed"
      return (
        <span className={isOverdue ? "text-destructive font-medium" : ""}>
          {date.toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </span>
      )
    },
  },
  {
    accessorKey: "progress",
    header: "Progress",
    cell: ({ row }) => {
      const { estimatedHours, completedHours } = row.original
      const percentage = Math.round((completedHours / estimatedHours) * 100)
      return (
        <div className="flex items-center gap-2">
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all"
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>
          <span className="text-xs text-muted-foreground min-w-[3rem]">
            {percentage}%
          </span>
        </div>
      )
    },
  },
  {
    accessorKey: "hours",
    header: "Hours",
    cell: ({ row }) => {
      const { estimatedHours, completedHours } = row.original
      return (
        <span className="text-sm">
          {completedHours}/{estimatedHours}h
        </span>
      )
    },
  },
]

export const Route = createFileRoute("/_horizontal-layout/item3")({
  component: Item3Page,
  head: () => ({
    meta: [
      {
        title: "Item 3 - Portal Dashboard",
      },
    ],
  }),
})

function Item3Page() {
  const [searchValue, setSearchValue] = useState("")
  const [filteredData, setFilteredData] = useState(taskData)

  const handleSearch = (value: string) => {
    setSearchValue(value)
    if (value.trim() === "") {
      setFilteredData(taskData)
    } else {
      const filtered = taskData.filter(
        (item) =>
          item.title.toLowerCase().includes(value.toLowerCase()) ||
          item.assignee.toLowerCase().includes(value.toLowerCase())
      )
      setFilteredData(filtered)
    }
  }

  const handleFilterApply = (filters: Record<string, any>) => {
    let filtered = taskData

    if (filters.status) {
      filtered = filtered.filter((item) => item.status === filters.status)
    }
    if (filters.priority) {
      filtered = filtered.filter((item) => item.priority === filters.priority)
    }
    if (filters.assignee) {
      filtered = filtered.filter((item) =>
        item.assignee.toLowerCase().includes(filters.assignee.toLowerCase())
      )
    }

    if (searchValue.trim() !== "") {
      filtered = filtered.filter(
        (item) =>
          item.title.toLowerCase().includes(searchValue.toLowerCase()) ||
          item.assignee.toLowerCase().includes(searchValue.toLowerCase())
      )
    }

    setFilteredData(filtered)
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Item 3 - Task Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Monitor and manage all tasks across teams
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Task Board</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <FilterBar
            config={{
              showTotalItems: true,
              showItemsPerPage: true,
              showSearchBox: true,
              showFilterButton: true,
              showCreateButton: true,
              searchPlaceholder: "Search tasks...",
              createButtonLabel: "New Task",
              advancedFilters: [
                {
                  name: "status",
                  label: "Status",
                  type: "select",
                  options: [
                    { label: "To Do", value: "todo" },
                    { label: "In Progress", value: "in-progress" },
                    { label: "Review", value: "review" },
                    { label: "Completed", value: "completed" },
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
                  name: "assignee",
                  label: "Assignee",
                  type: "text",
                  placeholder: "Enter assignee name...",
                },
                {
                  name: "dueDate",
                  label: "Due Date",
                  type: "date",
                },
              ],
            }}
            totalItems={filteredData.length}
            itemsPerPage={10}
            searchValue={searchValue}
            onSearchChange={handleSearch}
            onCreateClick={() => alert("Create new task clicked!")}
            onFilterApply={handleFilterApply}
          />

          <EnhancedDataTable
            columns={taskColumns}
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
