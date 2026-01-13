import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowLeft } from "lucide-react"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { tableData1 } from "@/data/tableData1"
import { statusVariants } from "@/lib/constants"
import { getInitials } from "@/lib/utils"

export const Route = createFileRoute("/_layout/table1/$id")({
  component: TeamMemberDetail,
  head: () => ({
    meta: [
      {
        title: "Team Member Detail - Engineering",
      },
    ],
  }),
})

function TeamMemberDetail() {
  const { id } = Route.useParams()
  const user = tableData1.find((item) => item.id === id)

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <h2 className="text-2xl font-bold">Team Member Not Found</h2>
        <p className="text-muted-foreground">
          The team member with ID {id} does not exist.
        </p>
        <Button asChild>
          <Link to="/table1">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Engineering Team
          </Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" asChild>
          <Link to="/table1">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Engineering Team
          </Link>
        </Button>
      </div>

      <div>
        <h1 className="text-4xl font-bold tracking-tight">
          Team Member Details
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">
          Detailed information for {user.name}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* User Profile Card */}
        <Card>
          <CardHeader>
            <CardTitle>Profile Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center gap-4">
              <Avatar className="h-20 w-20">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback className="text-2xl">
                  {getInitials(user.name)}
                </AvatarFallback>
              </Avatar>
              <div>
                <h3 className="text-2xl font-semibold">{user.name}</h3>
                <p className="text-muted-foreground">{user.email}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-sm font-medium text-muted-foreground">
                  Status
                </span>
                <div className="mt-1">
                  <Badge
                    variant="outline"
                    className={statusVariants[user.status]}
                  >
                    {user.status.charAt(0).toUpperCase() + user.status.slice(1)}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contact Information Card */}
        <Card>
          <CardHeader>
            <CardTitle>Contact Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <span className="text-sm font-medium text-muted-foreground">
                Email
              </span>
              <p className="mt-1 text-base">{user.email}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-muted-foreground">
                Phone
              </span>
              <p className="mt-1 text-base">{user.phone}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-muted-foreground">
                Location
              </span>
              <p className="mt-1 text-base">{user.location}</p>
            </div>
          </CardContent>
        </Card>

        {/* Work Information Card */}
        <Card>
          <CardHeader>
            <CardTitle>Work Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <span className="text-sm font-medium text-muted-foreground">
                Role
              </span>
              <p className="mt-1 text-base">{user.role}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-muted-foreground">
                Department
              </span>
              <p className="mt-1 text-base">{user.department}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-muted-foreground">
                Join Date
              </span>
              <p className="mt-1 text-base">
                {new Date(user.joinDate).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>
            <div>
              <span className="text-sm font-medium text-muted-foreground">
                Last Active
              </span>
              <p className="mt-1 text-base">
                {new Date(user.lastActive).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
