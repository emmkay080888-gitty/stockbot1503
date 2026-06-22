import { Suspense } from "react";
import { prisma } from "@/lib/prisma";
import { GameCard } from "@/components/games/GameCard";
import { GameFilters } from "@/components/games/GameFilters";
import { Skeleton } from "@/components/ui/skeleton";
import { SortSelect } from "./SortSelect";

interface GamesPageProps {
  searchParams: Promise<{ q?: string; genres?: string; featured?: string; sort?: string }>;
}

interface GamesGridProps {
  q?: string;
  genres?: string;
  featured?: string;
  sort?: string;
}

async function GamesGrid({ q, genres, featured, sort }: GamesGridProps) {
  const genreSlugs = genres?.split(",").filter(Boolean) || [];
  const isFeatured = featured === "true";
  const sortOrder = sort || "newest";

  const where: Record<string, unknown> = {};

  if (q) {
    where.title = { contains: q, mode: "insensitive" };
  }

  if (genreSlugs.length > 0) {
    where.genres = {
      some: {
        genre: {
          slug: { in: genreSlugs },
        },
      },
    };
  }

  if (isFeatured) {
    where.featured = true;
  }

  const orderBy: Record<string, "asc" | "desc"> =
    sortOrder === "popular" ? { downloadCount: "desc" as const } : { createdAt: "desc" as const };

  const games = await prisma.game.findMany({
    where,
    orderBy,
    include: {
      genres: { include: { genre: true } },
    },
    take: 24,
  });

  if (games.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="mb-4 text-4xl">🎮</div>
        <h3 className="text-lg font-semibold text-zinc-300">No games found</h3>
        <p className="mt-2 text-sm text-zinc-500">
          Try adjusting your search or filter criteria
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {games.map((game) => (
        <GameCard
          key={game.id}
          id={game.id}
          title={game.title}
          slug={game.slug}
          coverImage={game.coverImage}
          developer={game.developer}
          averageRating={game.averageRating}
          modCount={game.modCount}
          genres={game.genres}
        />
      ))}
    </div>
  );
}

function GamesGridSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900">
          <Skeleton className="aspect-[16/9] rounded-none bg-zinc-800" />
          <div className="space-y-3 p-4">
            <Skeleton className="h-4 w-3/4 bg-zinc-800" />
            <Skeleton className="h-3 w-1/2 bg-zinc-800" />
            <div className="flex gap-2">
              <Skeleton className="h-5 w-16 rounded-full bg-zinc-800" />
              <Skeleton className="h-5 w-12 rounded-full bg-zinc-800" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default async function GamesPage({ searchParams }: GamesPageProps) {
  const genres = await prisma.genre.findMany({
    orderBy: { name: "asc" },
  });

  const resolvedParams = await searchParams;
  const featured = resolvedParams.featured === "true";
  const sort = resolvedParams.sort || "newest";

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">
          {featured ? "Featured Mods" : "Game Library"}
        </h1>
        <p className="mt-2 text-zinc-400">
          {featured
            ? "Discover our hand-picked selection of the best mods"
            : "Browse our collection of games and their mods"}
        </p>
      </div>

      <div className="flex flex-col gap-8 lg:flex-row">
        {/* Sidebar filters */}
        <aside className="w-full lg:w-64 lg:flex-shrink-0">
          <GameFilters genres={genres} />
        </aside>

        {/* Main content */}
        <div className="min-w-0 flex-1">
          {/* Sort bar */}
          <div className="mb-6 flex items-center justify-between">
            <p className="text-sm text-zinc-500">
              Showing games
            </p>
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-500">Sort:</span>
              <SortSelect currentSort={sort} />
            </div>
          </div>

          <Suspense fallback={<GamesGridSkeleton />}>
            <GamesGrid
              q={resolvedParams.q}
              genres={resolvedParams.genres}
              featured={resolvedParams.featured}
              sort={resolvedParams.sort}
            />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
