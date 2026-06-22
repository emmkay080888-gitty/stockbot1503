import { redirect } from "next/navigation";
import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { auth } from "@/lib/auth";
import {
  User,
  Gamepad2,
  Download,
  Star,
  Settings,
  Sword,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ModCard } from "@/components/mods/ModCard";

export default async function ProfilePage() {
  const session = await auth();
  if (!session?.user?.id) {
    redirect("/login");
  }

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    include: {
      mods: {
        orderBy: { createdAt: "desc" },
        include: {
          game: { select: { slug: true } },
        },
        take: 10,
      },
      collections: {
        where: { isPublic: true },
        orderBy: { updatedAt: "desc" },
        take: 6,
      },
      _count: {
        select: {
          mods: true,
          collections: true,
          modReviews: true,
          favorites: true,
        },
      },
    },
  });

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Profile Header */}
      <div className="mb-8 rounded-xl border border-zinc-800 bg-zinc-900 p-6 sm:p-8">
        <div className="flex flex-col items-center gap-6 sm:flex-row">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-blue-600 text-2xl font-bold text-white">
            {user.name?.charAt(0) || "U"}
          </div>
          <div className="flex-1 text-center sm:text-left">
            <h1 className="text-2xl font-bold text-white">
              {user.name || "User"}
            </h1>
            <p className="mt-1 text-sm text-zinc-500">{user.email}</p>
            {user.bio && (
              <p className="mt-2 text-sm text-zinc-400">{user.bio}</p>
            )}
            <div className="mt-3 flex justify-center gap-4 sm:justify-start">
              <div className="text-center">
                <p className="text-lg font-bold text-white">
                  {user._count.mods}
                </p>
                <p className="text-xs text-zinc-500">Mods</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-white">
                  {user._count.collections}
                </p>
                <p className="text-xs text-zinc-500">Collections</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-white">
                  {user._count.modReviews}
                </p>
                <p className="text-xs text-zinc-500">Reviews</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-white">
                  {user._count.favorites}
                </p>
                <p className="text-xs text-zinc-500">Favorites</p>
              </div>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="rounded-full border-zinc-700 text-zinc-400 hover:bg-zinc-800 hover:text-white"
          >
            <Settings className="mr-2 h-4 w-4" />
            Edit Profile
          </Button>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1fr_300px]">
        {/* Main content */}
        <div>
          {/* My Mods */}
          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">
                My Mods
              </h2>
              {user.mods.length > 0 && (
                <Link
                  href="/profile/mods"
                  className="text-sm text-purple-400 hover:text-purple-300"
                >
                  View all
                </Link>
              )}
            </div>

            {user.mods.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 py-16 text-center">
                <Gamepad2 className="mb-3 h-8 w-8 text-zinc-700" />
                <p className="text-sm text-zinc-500">No mods created yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {user.mods.map((mod) => (
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
                    author={{ name: user.name, image: user.image }}
                    gameSlug={mod.game.slug}
                  />
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Sidebar */}
        <aside className="space-y-6">
          {/* Collections */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-zinc-300">
                Collections
              </h3>
              <Link
                href="/profile/collections"
                className="text-xs text-purple-400 hover:text-purple-300"
              >
                Manage
              </Link>
            </div>

            {user.collections.length === 0 ? (
              <p className="text-sm text-zinc-500">No collections yet</p>
            ) : (
              <div className="space-y-2">
                {user.collections.map((collection) => (
                  <Link
                    key={collection.id}
                    href={`/collections/${collection.id}`}
                    className="flex items-center gap-3 rounded-lg bg-zinc-800/50 p-3 transition-colors hover:bg-zinc-800"
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10">
                      <Sword className="h-4 w-4 text-purple-400" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-zinc-300">
                        {collection.name}
                      </p>
                      <p className="text-xs text-zinc-600">
                        Updated{" "}
                        {collection.updatedAt.toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                        })}
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Quick stats */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
            <h3 className="mb-4 text-sm font-semibold text-zinc-300">
              Activity
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10">
                  <Download className="h-4 w-4 text-purple-400" />
                </div>
                <div>
                  <p className="text-zinc-300">
                    {user.mods.reduce((sum, m) => sum + m.downloads, 0)} total
                    downloads
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-yellow-500/10">
                  <Star className="h-4 w-4 text-yellow-400" />
                </div>
                <div>
                  <p className="text-zinc-300">
                    {user._count.modReviews} reviews written
                  </p>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
