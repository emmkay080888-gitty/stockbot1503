import { notFound } from "next/navigation";
import Image from "next/image";
import { prisma } from "@/lib/prisma";
import { Gamepad2, Star, Download, Calendar, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ModCard } from "@/components/mods/ModCard";

interface GameDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function GameDetailPage({ params }: GameDetailPageProps) {
  const { slug } = await params;

  const game = await prisma.game.findUnique({
    where: { slug },
    include: {
      genres: { include: { genre: true } },
      mods: {
        where: { status: "APPROVED" },
        orderBy: { downloads: "desc" },
        include: {
          author: { select: { name: true, image: true } },
        },
        take: 20,
      },
    },
  });

  if (!game) {
    notFound();
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Hero Banner */}
      <div className="relative mb-8 overflow-hidden rounded-2xl">
        {/* Background */}
        <div className="aspect-[21/9] bg-gradient-to-br from-zinc-800 to-zinc-900">
          {game.bannerImage ? (
            <Image
              src={game.bannerImage}
              alt={game.title}
              fill
              className="object-cover opacity-50"
              priority
            />
          ) : game.coverImage ? (
            <Image
              src={game.coverImage}
              alt={game.title}
              fill
              className="object-cover opacity-40"
              priority
            />
          ) : null}
          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent" />
        </div>

        {/* Content overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-8">
          <div className="flex items-end gap-6">
            {/* Cover */}
            <div className="hidden h-32 w-24 flex-shrink-0 overflow-hidden rounded-lg bg-zinc-800 shadow-lg sm:block">
              {game.coverImage ? (
                <Image
                  src={game.coverImage}
                  alt={game.title}
                  width={96}
                  height={128}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex h-full items-center justify-center">
                  <Gamepad2 className="h-8 w-8 text-zinc-600" />
                </div>
              )}
            </div>

            <div className="flex-1">
              <h1 className="text-3xl font-bold text-white sm:text-4xl">
                {game.title}
              </h1>
              <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-zinc-400">
                <span>{game.developer}</span>
                {game.publisher && (
                  <>
                    <span className="text-zinc-600">·</span>
                    <span>{game.publisher}</span>
                  </>
                )}
                {game.releaseDate && (
                  <>
                    <span className="text-zinc-600">·</span>
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {game.releaseDate.getFullYear()}
                    </span>
                  </>
                )}
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-1 text-sm text-yellow-400">
                  <Star className="h-4 w-4 fill-yellow-400" />
                  <span className="font-medium">
                    {game.averageRating.toFixed(1)}
                  </span>
                </div>
                <span className="flex items-center gap-1 text-sm text-zinc-500">
                  <Download className="h-4 w-4" />
                  {game.downloadCount.toLocaleString()} downloads
                </span>
                <span className="flex items-center gap-1 text-sm text-zinc-500">
                  <Users className="h-4 w-4" />
                  {game.mods.length} mods
                </span>
              </div>

              <div className="mt-3 flex flex-wrap gap-2">
                {game.genres.map((g) => (
                  <Badge
                    key={g.genre.slug}
                    variant="secondary"
                    className="bg-zinc-800 text-xs text-zinc-400"
                  >
                    {g.genre.name}
                  </Badge>
                ))}
                {game.platforms.map((p) => (
                  <Badge
                    key={p}
                    className="border-zinc-700 bg-zinc-800/50 text-xs text-zinc-400"
                    variant="outline"
                  >
                    {p}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1fr_300px]">
        {/* Main content */}
        <div>
          {/* Description */}
          <section className="mb-8">
            <h2 className="mb-3 text-lg font-semibold text-white">
              About the Game
            </h2>
            <p className="leading-relaxed text-zinc-400">{game.description}</p>
          </section>

          {/* Mods List */}
          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Available Mods</h2>
              <p className="text-sm text-zinc-500">
                {game.mods.length} mod{game.mods.length !== 1 ? "s" : ""}
              </p>
            </div>

            {game.mods.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 py-16 text-center">
                <Gamepad2 className="mb-3 h-8 w-8 text-zinc-700" />
                <p className="text-sm text-zinc-500">No mods available yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {game.mods.map((mod) => (
                  <ModCard
                    key={mod.id}
                    id={mod.id}
                    title={mod.title}
                    slug={mod.slug}
                    type={mod.type}
                    imageUrl={mod.imageUrl}
                    shortDescription={mod.shortDescription}
                    downloads={mod.downloads}
                    views={mod.views}
                    likes={mod.likes}
                    version={mod.version}
                    verified={mod.verified}
                    author={mod.author}
                    gameSlug={game.slug}
                  />
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Sidebar */}
        <aside className="space-y-6">
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
            <h3 className="mb-4 text-sm font-semibold text-zinc-300">
              Game Info
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-zinc-500">Developer</span>
                <span className="text-zinc-300">{game.developer}</span>
              </div>
              {game.publisher && (
                <div className="flex justify-between">
                  <span className="text-zinc-500">Publisher</span>
                  <span className="text-zinc-300">{game.publisher}</span>
                </div>
              )}
              {game.releaseDate && (
                <div className="flex justify-between">
                  <span className="text-zinc-500">Release Date</span>
                  <span className="text-zinc-300">
                    {game.releaseDate.toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                    })}
                  </span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-zinc-500">Platforms</span>
                <span className="text-zinc-300">
                  {game.platforms.join(", ")}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Total Mods</span>
                <span className="text-zinc-300">{game.modCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Rating</span>
                <span className="flex items-center gap-1 text-yellow-400">
                  <Star className="h-3 w-3 fill-yellow-400" />
                  {game.averageRating.toFixed(1)}
                </span>
              </div>
            </div>
          </div>

          <Button className="w-full rounded-lg bg-purple-600 hover:bg-purple-700">
            <Download className="mr-2 h-4 w-4" />
            Browse All Mods
          </Button>
        </aside>
      </div>
    </div>
  );
}
