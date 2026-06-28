import { prisma } from "@/lib/prisma";
import Link from "next/link";
import { Gamepad2, Download, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { toggleGameFeatured } from "./actions";

export default async function AdminGamesPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;

  const games = await prisma.game.findMany({
    where: q
      ? {
          OR: [
            { title: { contains: q, mode: "insensitive" } },
            { developer: { contains: q, mode: "insensitive" } },
          ],
        }
      : undefined,
    orderBy: { createdAt: "desc" },
    include: {
      genres: { include: { genre: true } },
      _count: { select: { mods: true, reviews: true } },
    },
  });

  return (
    <div className="p-4 sm:p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Games</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Manage games on the platform
        </p>
      </div>

      {/* Search */}
      <form className="mb-6">
        <div className="relative max-w-md">
          <input
            type="text"
            name="q"
            defaultValue={q || ""}
            placeholder="Search games..."
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

      {/* Games table */}
      <div className="overflow-hidden rounded-xl border border-zinc-800">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900">
                <th className="px-4 py-3 text-left font-medium text-zinc-500">
                  Game
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">
                  Developer
                </th>
                <th className="px-4 py-3 text-center font-medium text-zinc-500">
                  Mods
                </th>
                <th className="px-4 py-3 text-center font-medium text-zinc-500">
                  Rating
                </th>
                <th className="px-4 py-3 text-center font-medium text-zinc-500">
                  Featured
                </th>
                <th className="px-4 py-3 text-right font-medium text-zinc-500">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {games.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-12 text-center text-sm text-zinc-600"
                  >
                    No games found
                  </td>
                </tr>
              ) : (
                games.map((game) => (
                  <tr
                    key={game.id}
                    className="bg-zinc-900/50 transition-colors hover:bg-zinc-800/50"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-800">
                          <Gamepad2 className="h-4 w-4 text-zinc-500" />
                        </div>
                        <div className="min-w-0">
                          <Link
                            href={`/games/${game.slug}`}
                            className="font-medium text-zinc-200 hover:text-purple-400"
                          >
                            {game.title}
                          </Link>
                          <div className="flex gap-1">
                            {game.genres.map((g) => (
                              <span
                                key={g.genre.slug}
                                className="text-[10px] text-zinc-600"
                              >
                                {g.genre.name}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-zinc-400">
                      {game.developer}
                    </td>
                    <td className="px-4 py-3 text-center text-zinc-400">
                      {game._count.mods}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {game.averageRating > 0 ? (
                        <span className="flex items-center justify-center gap-1 text-yellow-400">
                          <Star className="h-3 w-3 fill-yellow-400" />
                          {game.averageRating.toFixed(1)}
                        </span>
                      ) : (
                        <span className="text-zinc-600">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {game.featured ? (
                        <Badge className="bg-emerald-500/10 text-[10px] text-emerald-400">
                          Featured
                        </Badge>
                      ) : (
                        <span className="text-zinc-600">No</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <form action={toggleGameFeatured}>
                          <input
                            type="hidden"
                            name="gameId"
                            value={game.id}
                          />
                          <input
                            type="hidden"
                            name="featured"
                            value={game.featured ? "false" : "true"}
                          />
                          <Button
                            type="submit"
                            variant="ghost"
                            size="xs"
                            className="text-zinc-500 hover:text-yellow-400"
                          >
                            {game.featured ? "Unfeature" : "Feature"}
                          </Button>
                        </form>
                        <Link
                          href={`/games/${game.slug}`}
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
