import Link from "next/link";
import Image from "next/image";
import { Star, Download, Eye, ThumbsUp, Gamepad2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface ModCardProps {
  id: string;
  title: string;
  slug: string;
  type: string;
  imageUrl: string | null;
  shortDescription: string | null;
  downloads: number;
  views: number;
  likes: number;
  version: string;
  verified: boolean;
  author: { name: string | null; image: string | null };
  gameSlug: string;
}

export function ModCard({
  title,
  slug,
  type,
  imageUrl,
  shortDescription,
  downloads,
  views,
  likes,
  version,
  verified,
  author,
  gameSlug,
}: ModCardProps) {
  const typeColors: Record<string, string> = {
    TRAINER: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    CHEAT: "bg-red-500/10 text-red-400 border-red-500/20",
    OVERLAY: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    QOL: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    UI: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    FIX: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    CONTENT: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  };

  return (
    <Link href={`/games/${gameSlug}/mods/${slug}`} className="group block">
      <div className="flex gap-4 rounded-xl border border-zinc-800 bg-zinc-900 p-4 transition-all duration-300 hover:border-purple-500/30 hover:bg-zinc-800/80">
        {/* Thumbnail */}
        <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg bg-zinc-800">
          {imageUrl ? (
            <Image
              src={imageUrl}
              alt={title}
              fill
              className="object-cover"
              sizes="80px"
            />
          ) : (
            <div className="flex h-full items-center justify-center">
              <Gamepad2 className="h-6 w-6 text-zinc-700" />
            </div>
          )}
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-2">
            <h3 className="truncate text-sm font-semibold text-white group-hover:text-purple-400">
              {title}
            </h3>
            {verified && (
              <Badge className="bg-blue-500/10 px-1.5 py-0 text-[10px] text-blue-400">
                Verified
              </Badge>
            )}
          </div>

          <p className="mb-2 line-clamp-1 text-xs text-zinc-500">
            {shortDescription || "No description"}
          </p>

          <div className="flex flex-wrap items-center gap-3 text-xs text-zinc-500">
            <Badge
              variant="outline"
              className={`border px-1.5 py-0 text-[10px] ${
                typeColors[type] || "bg-zinc-500/10 text-zinc-400"
              }`}
            >
              {type}
            </Badge>
            <span>v{version}</span>
            <span className="flex items-center gap-1">
              <Download className="h-3 w-3" /> {formatNumber(downloads)}
            </span>
            <span className="flex items-center gap-1">
              <Eye className="h-3 w-3" /> {formatNumber(views)}
            </span>
            <span className="flex items-center gap-1">
              <ThumbsUp className="h-3 w-3" /> {formatNumber(likes)}
            </span>
            <span className="text-zinc-600">by {author.name || "Unknown"}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}

function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toString();
}
