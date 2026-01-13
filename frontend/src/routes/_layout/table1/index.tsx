import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { TableList } from "@/components/Common/TableList"
import { tableData1 } from "@/data/tableData1"

export const Route = createFileRoute("/_layout/table1/")({
  component: EngineeringTeam,
  head: () => ({
    meta: [
      {
        title: "Engineering Team - Portal",
      },
    ],
  }),
})

function EngineeringTeam() {
  const navigate = useNavigate()

  const handleNavigateToDetail = (id: string) => {
    navigate({ to: "/table1/$id", params: { id } })
  }

  return (
    <TableList
      title="Engineering Team"
      description="View and manage engineering team members"
      data={tableData1}
      navigateToDetail={handleNavigateToDetail}
      filterConfig={{
        departmentOptions: [
          { label: "Engineering", value: "Engineering" },
          { label: "Product", value: "Product" },
          { label: "Design", value: "Design" },
        ],
      }}
    />
  )
}
