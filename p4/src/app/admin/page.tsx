import { prisma } from "@/lib/prisma";
import Link from "next/link";
import {
  Gamepad2,
  Puzzle,
  Users,
  Download,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

async function getStats() {
  const [
    gameCount,
    modCount,
    userCount,
    totalDownloads,
    pendingMods,
    recentMods,
    recentUsers,
  ] = await Promise.all([
    prisma.game.count(),
    prisma.mod.count(),
    prisma.user.count(),
    prisma.mod.aggregate({ _sum: { downloads: true } }),
    prisma.mod.count({ where: { status: "PENDING" } }),
    prisma.mod.findMany({
      orderBy: { createdAt: "desc" },
      take: 5,
      include: {
        game: { select: { title: true, slug: true } },
        author: { select: { name: true, email: true } },
      },
    }),
    prisma.user.findMany({
      orderBy: { createdAt: "desc" },
      take: 5,
      select: {
        id: true,
        name: true,
        email: true,
        role: true,
        createdAt: true,
      },
    }),
  ]);

  return {
    gameCount,
    modCount,
    userCount,
    totalDownloads: totalDownloads._sum.downloads || 0,
    pendingMods,
    recentMods,
    recentUsers,
  };
}

export default async function AdminDashboardPage() {
  const stats = await getStats();

  const statCards = [
    {
      label: "Total Games",
      value: stats.gameCount,
      icon: Gamepad2,
      color: "from-blue-500 to-blue-600",
      bg: "bg-blue-500/10",
    },
    {
      label: "Total Mods",
      value: stats.modCount,
      icon: Puzzle,
      color: "from-purple-500 to-purple-600",
      bg: "bg-purple-500/10",
    },
    {
      label: "Total Users",
      value: stats.userCount,
      icon: Users,
      color: "from-emerald-500 to-emerald-600",
      bg: "bg-emerald-500/10",
    },
    {
      label: "Total Downloads",
      value: formatNumber(stats.totalDownloads),
      icon: Download,
      color: "from-orange-500 to-orange-600",
      bg: "bg-orange-500/10",
    },
  ];

  return (
    <div className="p-4 sm:p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Manage your ModHub platform
        </p>
      </div>

      {/* Stat Cards */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border border-zinc-800 bg-zinc-900 p-5"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-zinc-500">{card.label}</p>
                <p className="mt-1 text-2xl font-bold text-white">
                  {card.value}
                </p>
              </div>
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-xl ${card.bg}`}
              >
                <card.icon
                  className={`h-6 w-6 bg-gradient-to-br ${card.color} bg-clip-text text-transparent`}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Mods */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900">
          <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-4">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-zinc-500" />
              <h2 className="text-sm font-semibold text-white">Recent Mods</h2>
            </div>
            <Link
              href="/admin/mods"
              className="text-xs text-purple-400 hover:text-purple-300"
            >
              View all
            </Link>
          </div>
          <div className="divide-y divide-zinc-800">
            {stats.recentMods.length === 0 ? (
              <div className="flex items-center justify-center py-12 text-sm text-zinc-600">
                No mods uploaded yet
              </div>
            ) : (
              stats.recentMods.map((mod) => (
                <div
                  key={mod.id}
                  className="flex items-center justify-between px-5 py-3 text-sm"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-zinc-300">
                      {mod.title}
                    </p>
                    <p className="truncate text-xs text-zinc-600">
                      in {mod.game.title} by{" "}
                      {mod.author.name || mod.author.email || "Unknown"}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    {mod.status === "PENDING" ? (
                      <span className="flex items-center gap-1 text-xs text-yellow-400">
                        <AlertCircle className="h-3 w-3" />
                        Pending
                      </span>
                    ) : mod.status === "APPROVED" ? (
                      <span className="flex items-center gap-1 text-xs text-emerald-400">
                        <CheckCircle className="h-3 w-3" />
                        Approved
                      </span>
                    ) : (
                      <span className="text-xs text-red-400">Rejected</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Users */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900">
          <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-4">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-zinc-500" />
              <h2 className="text-sm font-semibold text-white">Recent Users</h2>
            </div>
            <Link
              href="/admin/users"
              className="text-xs text-purple-400 hover:text-purple-300"
            >
              View all
            </Link>
          </div>
          <div className="divide-y divide-zinc-800">
            {stats.recentUsers.length === 0 ? (
              <div className="flex items-center justify-center py-12 text-sm text-zinc-600">
                No users registered yet
              </div>
            ) : (
              stats.recentUsers.map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between px-5 py-3 text-sm"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-zinc-300">
                      {user.name || "Unnamed"}
                    </p>
                    <p className="truncate text-xs text-zinc-600">
                      {user.email}
                    </p>
                  </div>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                      user.role === "ADMIN"
                        ? "bg-purple-500/10 text-purple-400"
                        : user.role === "MODDER"
                          ? "bg-blue-500/10 text-blue-400"
                          : "bg-zinc-500/10 text-zinc-400"
                    }`}
                  >
                    {user.role}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Pending Mods Alert */}
        {stats.pendingMods > 0 && (
          <div className="lg:col-span-2">
            <Link
              href="/admin/mods?status=PENDING"
              className="flex items-center gap-3 rounded-xl border border-yellow-500/20 bg-yellow-500/5 px-5 py-4 transition-colors hover:bg-yellow-500/10"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-yellow-500/10">
                <AlertCircle className="h-5 w-5 text-yellow-400" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-yellow-300">
                  {stats.pendingMods} mod{stats.pendingMods !== 1 ? "s" : ""}{" "}
                  pending review
                </p>
                <p className="text-xs text-yellow-500/70">
                  Review and approve or reject these submissions
                </p>
              </div>
              <TrendingUp className="h-4 w-4 text-yellow-500" />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toString();
}
