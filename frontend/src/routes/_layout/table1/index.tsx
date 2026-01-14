import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { Pencil, Trash2 } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { TableList } from "@/components/Common/TableList"
import { AddMemberModal } from "@/components/Table1/AddMemberModal"
import { DeleteMemberDialog } from "@/components/Table1/DeleteMemberDialog"
import { EditMemberModal } from "@/components/Table1/EditMemberModal"
import { Button } from "@/components/ui/button"
import { tableData1 } from "@/data/tableData1"
import { fakeApiService, type TeamMember } from "@/services/fakeApi"

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
  const [data, setData] = useState<TeamMember[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null)

  const loadData = useCallback(async () => {
    setIsLoading(true)
    try {
      const members = await fakeApiService.getAll()
      setData(members)
    } catch (error) {
      console.error("Failed to load members:", error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fakeApiService.initializeData(tableData1)
    loadData()
  }, [loadData])

  const handleNavigateToDetail = (id: string) => {
    navigate({ to: "/table1/$id", params: { id } })
  }

  const handleEdit = (member: TeamMember) => {
    setSelectedMember(member)
    setShowEditModal(true)
  }

  const handleDelete = (member: TeamMember) => {
    setSelectedMember(member)
    setShowDeleteDialog(true)
  }

  const actionColumn = {
    id: "actions",
    header: "Actions",
    cell: ({ row }: { row: { original: TeamMember } }) => (
      <div className="flex gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation()
            handleEdit(row.original)
          }}
        >
          <Pencil className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation()
            handleDelete(row.original)
          }}
        >
          <Trash2 className="h-4 w-4 text-destructive" />
        </Button>
      </div>
    ),
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">Loading...</div>
    )
  }

  return (
    <>
      <TableList
        title="Engineering Team"
        description="View and manage engineering team members"
        data={data}
        navigateToDetail={handleNavigateToDetail}
        filterConfig={{
          departmentOptions: [
            { label: "Engineering", value: "Engineering" },
            { label: "Product", value: "Product" },
            { label: "Design", value: "Design" },
          ],
        }}
        actionColumn={actionColumn}
        onCreateClick={() => setShowAddModal(true)}
      />

      <AddMemberModal
        open={showAddModal}
        onOpenChange={setShowAddModal}
        onSuccess={loadData}
      />

      <EditMemberModal
        open={showEditModal}
        onOpenChange={setShowEditModal}
        member={selectedMember}
        onSuccess={loadData}
      />

      <DeleteMemberDialog
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        member={selectedMember}
        onSuccess={loadData}
      />
    </>
  )
}
