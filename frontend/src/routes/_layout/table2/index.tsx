import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { TableList } from "@/components/Common/TableList"
import { tableData2 } from "@/data/tableData2"

export const Route = createFileRoute("/_layout/table2/")({
  component: BusinessTeam,
  head: () => ({
    meta: [
      {
        title: "Business Team - Portal",
      },
    ],
  }),
})

function BusinessTeam() {
  const navigate = useNavigate()

  const handleNavigateToDetail = (id: string) => {
    navigate({ to: "/table2/$id", params: { id } })
  }

  return (
    <TableList
      title="Business Team"
      description="View and manage business team members"
      data={tableData2}
      navigateToDetail={handleNavigateToDetail}
      filterConfig={{
        departmentOptions: [
          { label: "Marketing", value: "Marketing" },
          { label: "Analytics", value: "Analytics" },
          { label: "Human Resources", value: "Human Resources" },
        ],
      }}
    />
  )
}
