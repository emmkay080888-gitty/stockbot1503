import Link from "next/link";
import Image from "next/image";
import { Star, Download, Gamepad2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface GameCardProps {
  id: string;
  title: string;
  slug: string;
  coverImage: string | null;
  developer: string;
  averageRating: number;
  modCount: number;
  genres: { genre: { name: string; slug: string } }[];
}

export function GameCard({
  title,
  slug,
  coverImage,
  developer,
  averageRating,
  modCount,
  genres,
}: GameCardProps) {
  return (
    <Link href={`/games/${slug}`} className="group block">
      <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900 transition-all duration-300 hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10">
        {/* Cover Image */}
        <div className="relative aspect-[16/9] overflow-hidden bg-zinc-800">
          {coverImage ? (
            <Image
              src={coverImage}
              alt={title}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-105"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <div className="flex h-full items-center justify-center">
              <Gamepad2 className="h-12 w-12 text-zinc-700" />
            </div>
          )}
          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-transparent to-transparent" />

          {/* Rating badge */}
          {averageRating > 0 && (
            <div className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-1 text-xs font-medium text-yellow-400 backdrop-blur-sm">
              <Star className="h-3 w-3 fill-yellow-400" />
              {averageRating.toFixed(1)}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          <h3 className="mb-1 truncate text-base font-semibold text-white group-hover:text-purple-400">
            {title}
          </h3>
          <p className="mb-3 text-sm text-zinc-500">{developer}</p>

          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-1.5">
              {genres.slice(0, 2).map((g) => (
                <Badge
                  key={g.genre.slug}
                  variant="secondary"
                  className="bg-zinc-800 text-xs text-zinc-400"
                >
                  {g.genre.name}
                </Badge>
              ))}
            </div>
            <div className="flex items-center gap-1 text-xs text-zinc-500">
              <Download className="h-3 w-3" />
              <span>{modCount} mods</span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
