import { prisma } from "@/lib/prisma";
import Link from "next/link";
import { Puzzle, Download, Eye, ThumbsUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { updateModStatus } from "./actions";

const statusColors: Record<string, string> = {
  PENDING: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  APPROVED: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  REJECTED: "bg-red-500/10 text-red-400 border-red-500/20",
  DRAFT: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
  ARCHIVED: "bg-zinc-500/10 text-zinc-500 border-zinc-500/20",
};

interface PageProps {
  searchParams: Promise<{
    q?: string;
    status?: string;
  }>;
}

export default async function AdminModsPage({ searchParams }: PageProps) {
  const { q, status } = await searchParams;

  const where: Record<string, unknown> = {};
  if (q) {
    where.OR = [
      { title: { contains: q, mode: "insensitive" } },
    ];
  }
  if (status && ["PENDING", "APPROVED", "REJECTED", "DRAFT", "ARCHIVED"].includes(status)) {
    where.status = status;
  }

  const [mods, pendingCount] = await Promise.all([
    prisma.mod.findMany({
      where: where as any,
      orderBy: { createdAt: "desc" },
      take: 50,
      include: {
        game: { select: { title: true, slug: true } },
        author: { select: { name: true, email: true } },
      },
    }),
    prisma.mod.count({ where: { status: "PENDING" } }),
  ]);

  const statusFilters = ["ALL", "PENDING", "APPROVED", "REJECTED"];

  return (
    <div className="p-4 sm:p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Mods</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Review and manage mod submissions
        </p>
        {pendingCount > 0 && (
          <p className="mt-1 text-sm text-yellow-400">
            {pendingCount} mod{pendingCount !== 1 ? "s" : ""} pending review
          </p>
        )}
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <form className="relative max-w-xs">
          <input
            type="text"
            name="q"
            defaultValue={q || ""}
            placeholder="Search mods..."
            className="h-9 w-full rounded-lg border border-zinc-700 bg-zinc-800/50 pl-3 pr-8 text-sm text-zinc-300 placeholder:text-zinc-500 focus:border-purple-500 focus:outline-none"
          />
          <button
            type="submit"
            className="absolute right-1 top-1 rounded px-2 py-1 text-xs text-zinc-500 hover:text-zinc-300"
          >
            Go
          </button>
        </form>

        <div className="flex gap-1">
          {statusFilters.map((s) => (
            <Link
              key={s}
              href={
                s === "ALL"
                  ? "/admin/mods"
                  : `/admin/mods?status=${s}${q ? `&q=${q}` : ""}`
              }
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                (s === "ALL" && !status) || status === s
                  ? "bg-purple-500/10 text-purple-400"
                  : "text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300"
              }`}
            >
              {s === "ALL" ? "All" : s.charAt(0) + s.slice(1).toLowerCase()}
            </Link>
          ))}
        </div>
      </div>

      {/* Mods table */}
      <div className="overflow-hidden rounded-xl border border-zinc-800">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900">
                <th className="px-4 py-3 text-left font-medium text-zinc-500">
                  Mod
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">
                  Game
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">
                  Author
                </th>
                <th className="px-4 py-3 text-center font-medium text-zinc-500">
                  Status
                </th>
                <th className="px-4 py-3 text-center font-medium text-zinc-500">
                  Stats
                </th>
                <th className="px-4 py-3 text-right font-medium text-zinc-500">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {mods.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-12 text-center text-sm text-zinc-600"
                  >
                    No mods found
                  </td>
                </tr>
              ) : (
                mods.map((mod) => (
                  <tr
                    key={mod.id}
                    className="bg-zinc-900/50 transition-colors hover:bg-zinc-800/50"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-800">
                          <Puzzle className="h-4 w-4 text-zinc-500" />
                        </div>
                        <div className="min-w-0">
                          <Link
                            href={`/games/${mod.game.slug}/mods/${mod.slug}`}
                            className="font-medium text-zinc-200 hover:text-purple-400"
                          >
                            {mod.title}
                          </Link>
                          <p className="text-[10px] text-zinc-600">
                            v{mod.version} &middot;{" "}
                            {mod.type}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        href={`/games/${mod.game.slug}`}
                        className="text-zinc-400 hover:text-purple-400"
                      >
                        {mod.game.title}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-zinc-400">
                      {mod.author.name || mod.author.email || "Unknown"}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge
                        variant="outline"
                        className={`border px-2 py-0.5 text-[10px] ${
                          statusColors[mod.status] ||
                          "bg-zinc-500/10 text-zinc-400"
                        }`}
                      >
                        {mod.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-center gap-3 text-xs text-zinc-500">
                        <span className="flex items-center gap-1">
                          <Download className="h-3 w-3" />
                          {mod.downloads}
                        </span>
                        <span className="flex items-center gap-1">
                          <Eye className="h-3 w-3" />
                          {mod.views}
                        </span>
                        <span className="flex items-center gap-1">
                          <ThumbsUp className="h-3 w-3" />
                          {mod.likes}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        {mod.status === "PENDING" && (
                          <>
                            <form action={updateModStatus}>
                              <input
                                type="hidden"
                                name="modId"
                                value={mod.id}
                              />
                              <input
                                type="hidden"
                                name="status"
                                value="APPROVED"
                              />
                              <Button
                                type="submit"
                                variant="ghost"
                                size="xs"
                                className="text-emerald-500 hover:text-emerald-400"
                              >
                                Approve
                              </Button>
                            </form>
                            <form action={updateModStatus}>
                              <input
                                type="hidden"
                                name="modId"
                                value={mod.id}
                              />
                              <input
                                type="hidden"
                                name="status"
                                value="REJECTED"
                              />
                              <Button
                                type="submit"
                                variant="ghost"
                                size="xs"
                                className="text-red-500 hover:text-red-400"
                              >
                                Reject
                              </Button>
                            </form>
                          </>
                        )}
                        {mod.status === "APPROVED" && (
                          <form action={updateModStatus}>
                            <input
                              type="hidden"
                              name="modId"
                              value={mod.id}
                            />
                            <input
                              type="hidden"
                              name="status"
                              value="REJECTED"
                            />
                            <Button
                              type="submit"
                              variant="ghost"
                              size="xs"
                              className="text-red-500 hover:text-red-400"
                            >
                              Reject
                            </Button>
                          </form>
                        )}
                        {mod.status === "REJECTED" && (
                          <form action={updateModStatus}>
                            <input
                              type="hidden"
                              name="modId"
                              value={mod.id}
                            />
                            <input
                              type="hidden"
                              name="status"
                              value="APPROVED"
                            />
                            <Button
                              type="submit"
                              variant="ghost"
                              size="xs"
                              className="text-emerald-500 hover:text-emerald-400"
                            >
                              Approve
                            </Button>
                          </form>
                        )}
                        <Link
                          href={`/games/${mod.game.slug}/mods/${mod.slug}`}
                          className="rounded-md px-2 py-1 text-xs text-purple-400 hover:text-purple-300"
                        >
                          View
                        </Link>
                      </div>
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
