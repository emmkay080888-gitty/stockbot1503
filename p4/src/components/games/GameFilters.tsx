"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Search, SlidersHorizontal, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Genre {
  id: string;
  name: string;
  slug: string;
}

interface GameFiltersProps {
  genres: Genre[];
}

export function GameFilters({ genres }: GameFiltersProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("q") || "");
  const [selectedGenres, setSelectedGenres] = useState<string[]>(
    searchParams.get("genres")?.split(",").filter(Boolean) || []
  );
  const [showFilters, setShowFilters] = useState(false);

  const updateFilters = (newGenres: string[]) => {
    setSelectedGenres(newGenres);
    const params = new URLSearchParams();
    if (search) params.set("q", search);
    if (newGenres.length > 0) params.set("genres", newGenres.join(","));
    router.push(`/games?${params.toString()}`);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    updateFilters(selectedGenres);
  };

  const toggleGenre = (slug: string) => {
    const newGenres = selectedGenres.includes(slug)
      ? selectedGenres.filter((g) => g !== slug)
      : [...selectedGenres, slug];
    updateFilters(newGenres);
  };

  const clearFilters = () => {
    setSearch("");
    setSelectedGenres([]);
    router.push("/games");
  };

  const hasFilters = search || selectedGenres.length > 0;

  return (
    <div className="space-y-6">
      {/* Search */}
      <form onSubmit={handleSearch}>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
          <Input
            type="search"
            placeholder="Search games..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-10 w-full rounded-lg border-zinc-700 bg-zinc-900 pl-9 text-sm text-zinc-300 placeholder:text-zinc-500 focus:border-purple-500"
          />
        </div>
      </form>

      {/* Mobile filter toggle */}
      <button
        onClick={() => setShowFilters(!showFilters)}
        className="flex w-full items-center justify-between rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-2 text-sm text-zinc-400 lg:hidden"
      >
        <span className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4" />
          Filters
        </span>
        {hasFilters && (
          <Badge className="bg-purple-600 text-xs">
            {selectedGenres.length + (search ? 1 : 0)}
          </Badge>
        )}
      </button>

      {/* Filters */}
      <div className={`space-y-4 ${showFilters ? "block" : "hidden lg:block"}`}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-zinc-300">Genres</h3>
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-300"
            >
              <X className="h-3 w-3" />
              Clear
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          {genres.map((genre) => (
            <button
              key={genre.id}
              onClick={() => toggleGenre(genre.slug)}
              className={`rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
                selectedGenres.includes(genre.slug)
                  ? "bg-purple-600 text-white"
                  : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
              }`}
            >
              {genre.name}
            </button>
          ))}
        </div>

        {hasFilters && (
          <Button
            onClick={clearFilters}
            variant="outline"
            size="sm"
            className="w-full border-zinc-700 text-zinc-400 hover:bg-zinc-800 hover:text-white"
          >
            Clear All Filters
          </Button>
        )}
      </div>
    </div>
  );
}
