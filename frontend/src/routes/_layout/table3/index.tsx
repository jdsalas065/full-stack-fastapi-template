import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { TableList } from "@/components/Common/TableList"
import { tableData3 } from "@/data/tableData3"

export const Route = createFileRoute("/_layout/table3/")({
  component: SalesAndSupport,
  head: () => ({
    meta: [
      {
        title: "Sales & Support - Portal",
      },
    ],
  }),
})

function SalesAndSupport() {
  const navigate = useNavigate()

  const handleNavigateToDetail = (id: string) => {
    navigate({ to: "/table3/$id", params: { id } })
  }

  return (
    <TableList
      title="Sales & Support"
      description="View and manage sales and support team members"
      data={tableData3}
      navigateToDetail={handleNavigateToDetail}
      filterConfig={{
        departmentOptions: [
          { label: "Sales", value: "Sales" },
          { label: "Support", value: "Support" },
          { label: "Customer Success", value: "Customer Success" },
        ],
      }}
    />
  )
}
