import { prisma } from "@/lib/prisma";
import Link from "next/link";
import { Users, Shield, Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { updateUserRole } from "./actions";

interface PageProps {
  searchParams: Promise<{
    q?: string;
  }>;
}

export default async function AdminUsersPage({ searchParams }: PageProps) {
  const { q } = await searchParams;

  const users = await prisma.user.findMany({
    where: q
      ? {
          OR: [
            { name: { contains: q, mode: "insensitive" } },
            { email: { contains: q, mode: "insensitive" } },
          ],
        }
      : undefined,
    orderBy: { createdAt: "desc" },
    include: {
      _count: {
        select: {
          mods: true,
          collections: true,
          modReviews: true,
        },
      },
    },
  });

  const roleColors: Record<string, string> = {
    ADMIN: "bg-purple-500/10 text-purple-400",
    MODDER: "bg-blue-500/10 text-blue-400",
    USER: "bg-zinc-500/10 text-zinc-400",
  };

  return (
    <div className="p-4 sm:p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Users</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Manage platform users and roles
        </p>
        <p className="mt-1 text-xs text-zinc-600">
          {users.length} total users
        </p>
      </div>

      {/* Search */}
      <form className="mb-6">
        <div className="relative max-w-md">
          <input
            type="text"
            name="q"
            defaultValue={q || ""}
            placeholder="Search users by name or email..."
            className="h-10 w-full rounded-lg border border-zinc-700 bg-zinc-800/50 pl-4 pr-10 text-sm text-zinc-300 placeholder:text-zinc-500 focus:border-purple-500 focus:outline-none"
          />
          <button
            type="submit"
            className="absolute right-1 top-1 rounded-md px-3 py-1.5 text-xs text-zinc-500 hover:text-zinc-300"
          >
            Search
          </button>
        </div>
      </form>

      {/* Users table */}
      <div className="overflow-hidden rounded-xl border border-zinc-800">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900">
                <th className="px-4 py-3 text-left font-medium text-zinc-500">
                  User
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">
                  Role
                </th>
                <th className="px-4 py-3 text-center font-medium text-zinc-500">
                  Mods
                </th>
                <th className="px-4 py-3 text-center font-medium text-zinc-500">
                  Collections
                </th>
                <th className="px-4 py-3 text-center font-medium text-zinc-500">
                  Reviews
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">
                  Joined
                </th>
                <th className="px-4 py-3 text-right font-medium text-zinc-500">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {users.length === 0 ? (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-12 text-center text-sm text-zinc-600"
                  >
                    No users found
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr
                    key={user.id}
                    className="bg-zinc-900/50 transition-colors hover:bg-zinc-800/50"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-blue-600 text-xs font-bold text-white">
                          {user.name?.charAt(0)?.toUpperCase() || "?"}
                        </div>
                        <div className="min-w-0">
                          <p className="truncate font-medium text-zinc-200">
                            {user.name || "Unnamed"}
                          </p>
                          <p className="truncate text-xs text-zinc-600">
                            {user.email}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge
                        variant="outline"
                        className={`border px-2 py-0.5 text-[10px] ${
                          roleColors[user.role] || "bg-zinc-500/10 text-zinc-400"
                        }`}
                      >
                        {user.role}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-center text-zinc-400">
                      {user._count.mods}
                    </td>
                    <td className="px-4 py-3 text-center text-zinc-400">
                      {user._count.collections}
                    </td>
                    <td className="px-4 py-3 text-center text-zinc-400">
                      {user._count.modReviews}
                    </td>
                    <td className="px-4 py-3 text-zinc-500">
                      <div className="flex items-center gap-1.5">
                        <Calendar className="h-3 w-3" />
                        {user.createdAt.toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {user.role !== "ADMIN" && (
                        <div className="flex items-center justify-end gap-1">
                          <form action={updateUserRole}>
                            <input
                              type="hidden"
                              name="userId"
                              value={user.id}
                            />
                            <input
                              type="hidden"
                              name="role"
                              value={user.role === "MODDER" ? "USER" : "MODDER"}
                            />
                            <Button
                              type="submit"
                              variant="ghost"
                              size="xs"
                              className={
                                user.role === "MODDER"
                                  ? "text-zinc-500 hover:text-zinc-300"
                                  : "text-blue-500 hover:text-blue-400"
                              }
                            >
                              {user.role === "MODDER"
                                ? "Remove Modder"
                                : "Make Modder"}
                            </Button>
                          </form>
                        </div>
                      )}
                      {user.role === "ADMIN" && (
                        <span className="flex items-center justify-end gap-1 text-xs text-purple-500">
                          <Shield className="h-3 w-3" />
                          Protected
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
