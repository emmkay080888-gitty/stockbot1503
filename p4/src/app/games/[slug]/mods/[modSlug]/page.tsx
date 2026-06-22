import { notFound } from "next/navigation";
import Image from "next/image";
import { prisma } from "@/lib/prisma";
import {
  Download,
  Eye,
  ThumbsUp,
  Star,
  User,
  Calendar,
  Shield,
  Gamepad2,
  ArrowLeft,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { auth } from "@/lib/auth";
import Link from "next/link";

interface ModDetailPageProps {
  params: Promise<{ slug: string; modSlug: string }>;
}

const typeColors: Record<string, string> = {
  TRAINER: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  CHEAT: "bg-red-500/10 text-red-400 border-red-500/20",
  OVERLAY: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  QOL: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  UI: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  FIX: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  CONTENT: "bg-orange-500/10 text-orange-400 border-orange-500/20",
};

function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toString();
}

export default async function ModDetailPage({ params }: ModDetailPageProps) {
  const { slug, modSlug } = await params;
  const session = await auth();

  const mod = await prisma.mod.findUnique({
    where: { slug: modSlug },
    include: {
      game: { select: { title: true, slug: true, coverImage: true } },
      author: { select: { name: true, image: true } },
      tags: { include: { tag: true } },
      reviews: {
        include: {
          user: { select: { name: true, image: true } },
        },
        orderBy: { createdAt: "desc" },
        take: 10,
      },
    },
  });

  if (!mod || mod.game.slug !== slug) {
    notFound();
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Back link */}
      <Link
        href={`/games/${slug}`}
        className="mb-6 inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-300"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to {mod.game.title}
      </Link>

      <div className="grid gap-8 lg:grid-cols-[1fr_350px]">
        {/* Main content */}
        <div>
          {/* Title section */}
          <div className="mb-6">
            <div className="mb-2 flex items-center gap-2">
              <Badge
                variant="outline"
                className={`border px-2 py-0.5 text-xs ${
                  typeColors[mod.type] || "bg-zinc-500/10 text-zinc-400"
                }`}
              >
                {mod.type}
              </Badge>
              {mod.verified && (
                <Badge className="bg-blue-500/10 text-xs text-blue-400">
                  Verified
                </Badge>
              )}
              <Badge
                className={`text-xs ${
                  mod.status === "APPROVED"
                    ? "bg-emerald-500/10 text-emerald-400"
                    : "bg-yellow-500/10 text-yellow-400"
                }`}
              >
                {mod.status}
              </Badge>
            </div>
            <h1 className="text-3xl font-bold text-white">{mod.title}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-zinc-500">
              <span className="flex items-center gap-1">
                <User className="h-3 w-3" />
                {mod.author.name || "Unknown"}
              </span>
              <span>v{mod.version}</span>
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {mod.createdAt.toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </span>
            </div>

            {/* Tags */}
            {mod.tags.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {mod.tags.map((t) => (
                  <Badge
                    key={t.tag.slug}
                    variant="outline"
                    className="border-zinc-700 bg-zinc-800/50 text-[10px] text-zinc-500"
                  >
                    {t.tag.name}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Images */}
          {mod.images.length > 0 && (
            <div className="mb-8 grid gap-3 sm:grid-cols-2">
              {mod.images.slice(0, 4).map((img, i) => (
                <div
                  key={i}
                  className="relative aspect-video overflow-hidden rounded-lg bg-zinc-800"
                >
                  <Image
                    src={img}
                    alt={`${mod.title} screenshot ${i + 1}`}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 100vw, 50vw"
                  />
                </div>
              ))}
            </div>
          )}

          {/* Description */}
          <section className="mb-8">
            <h2 className="mb-3 text-lg font-semibold text-white">
              Description
            </h2>
            <div className="prose prose-sm prose-invert max-w-none leading-relaxed text-zinc-400">
              {mod.description.split("\n").map((line, i) => (
                <p key={i}>{line || "\u00A0"}</p>
              ))}
            </div>
          </section>

          {/* Reviews */}
          <section>
            <h2 className="mb-4 text-lg font-semibold text-white">
              Reviews ({mod.reviews.length})
            </h2>

            {mod.reviews.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 py-12 text-center">
                <Star className="mb-2 h-6 w-6 text-zinc-700" />
                <p className="text-sm text-zinc-500">No reviews yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {mod.reviews.map((review) => (
                  <div
                    key={review.id}
                    className="rounded-xl border border-zinc-800 bg-zinc-900 p-4"
                  >
                    <div className="mb-2 flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-600 text-xs font-medium text-white">
                        {review.user.name?.charAt(0) || "?"}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-zinc-300">
                          {review.user.name || "Anonymous"}
                        </p>
                        <div className="flex items-center gap-1">
                          {Array.from({ length: 5 }).map((_, i) => (
                            <Star
                              key={i}
                              className={`h-3 w-3 ${
                                i < review.rating
                                  ? "fill-yellow-400 text-yellow-400"
                                  : "text-zinc-700"
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                    {review.content && (
                      <p className="text-sm leading-relaxed text-zinc-400">
                        {review.content}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Sidebar */}
        <aside className="space-y-6">
          {/* Download card */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
            <div className="mb-6 flex items-center justify-around text-center">
              <div>
                <p className="text-2xl font-bold text-white">
                  {formatNumber(mod.downloads)}
                </p>
                <p className="text-xs text-zinc-500">Downloads</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">
                  {formatNumber(mod.views)}
                </p>
                <p className="text-xs text-zinc-500">Views</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">
                  {formatNumber(mod.likes)}
                </p>
                <p className="text-xs text-zinc-500">Likes</p>
              </div>
            </div>

            {mod.downloadUrl ? (
              <a
                href={mod.downloadUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 py-4 text-base font-medium text-white transition-all hover:from-purple-700 hover:to-blue-700"
              >
                <Download className="h-5 w-5" />
                Download v{mod.version}
              </a>
            ) : (
              <Button className="w-full cursor-not-allowed rounded-lg bg-zinc-800 py-6 text-base font-medium text-zinc-500">
                <Download className="mr-2 h-5 w-5" />
                Download Unavailable
              </Button>
            )}

            {mod.downloadUrl && (
              <p className="mt-2 text-center text-xs text-zinc-600">
                Hosted on Nexus Mods &middot;
                {mod.fileSize
                  ? ` ${(mod.fileSize / 1_000_000).toFixed(1)} MB`
                  : ""}
              </p>
            )}
          </div>

          {/* Info card */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
            <h3 className="mb-4 text-sm font-semibold text-zinc-300">
              Details
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-zinc-500">Type</span>
                <span className="text-zinc-300">{mod.type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Version</span>
                <span className="text-zinc-300">{mod.version}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Status</span>
                <span className="text-zinc-300">{mod.status}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Author</span>
                <span className="text-zinc-300">
                  {mod.author.name || "Unknown"}
                </span>
              </div>
              {mod.compatibility && (
                <div className="flex justify-between">
                  <span className="text-zinc-500">Compatibility</span>
                  <span className="text-zinc-300">{mod.compatibility}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-zinc-500">Created</span>
                <span className="text-zinc-300">
                  {mod.createdAt.toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Updated</span>
                <span className="text-zinc-300">
                  {mod.updatedAt.toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </span>
              </div>
            </div>
          </div>

          {/* Safety card */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
            <div className="flex items-start gap-3">
              <Shield className="mt-0.5 h-5 w-5 text-emerald-400" />
              <div>
                <h3 className="text-sm font-semibold text-zinc-300">
                  Safety Check
                </h3>
                <p className="mt-1 text-xs leading-relaxed text-zinc-500">
                  {mod.verified
                    ? "This mod has been verified by our community. It is safe to use."
                    : "This mod has not been verified yet. Use at your own discretion."}
                </p>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
