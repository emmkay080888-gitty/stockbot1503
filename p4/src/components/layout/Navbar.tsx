"use client";

import Link from "next/link";
import { useSession, signIn, signOut } from "next-auth/react";
import { useState } from "react";
import { Search, Gamepad2, Menu, X, User, LogOut, Sword, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function Navbar() {
  const { data: session, status } = useSession();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/games?q=${encodeURIComponent(searchQuery.trim())}`;
    }
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-zinc-800 bg-black/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-blue-600">
            <Sword className="h-4 w-4 text-white" />
          </div>
          <span className="text-lg font-bold text-white">ModHub</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden items-center gap-6 md:flex">
          <Link
            href="/games"
            className="text-sm font-medium text-zinc-400 transition-colors hover:text-white"
          >
            Game Library
          </Link>
          <Link
            href="/games?featured=true"
            className="text-sm font-medium text-zinc-400 transition-colors hover:text-white"
          >
            Featured Mods
          </Link>

          {/* Search */}
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
            <Input
              type="search"
              placeholder="Search games & mods..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-9 w-64 rounded-full border-zinc-700 bg-zinc-900 pl-9 text-sm text-zinc-300 placeholder:text-zinc-500 focus:border-purple-500 focus:ring-purple-500"
            />
          </form>
        </div>

        {/* User Menu */}
        <div className="flex items-center gap-3">
          {status === "authenticated" ? (
            <DropdownMenu>
              <DropdownMenuTrigger className="flex items-center gap-2 rounded-full outline-none transition-opacity hover:opacity-80">
                <Avatar className="h-8 w-8 border border-zinc-700">
                  <AvatarImage src={session.user?.image || ""} />
                  <AvatarFallback className="bg-purple-600 text-xs text-white">
                    {session.user?.name?.charAt(0) || "U"}
                  </AvatarFallback>
                </Avatar>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                className="w-56 border-zinc-800 bg-zinc-900 text-zinc-200"
              >
                <DropdownMenuLabel>
                  <div className="flex flex-col">
                    <span>{session.user?.name || "User"}</span>
                    <span className="text-xs font-normal text-zinc-500">
                      {session.user?.email}
                    </span>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-zinc-800" />
                {session.user?.role === "ADMIN" && (
                  <>
                    <DropdownMenuItem className="flex cursor-pointer items-center gap-2">
                      <Shield className="h-4 w-4 text-purple-400" />
                      <a href="/admin">Admin Dashboard</a>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator className="bg-zinc-800" />
                  </>
                )}
                <DropdownMenuItem className="flex cursor-pointer items-center gap-2">
                  <User className="h-4 w-4" />
                  <a href="/profile">Profile</a>
                </DropdownMenuItem>
                <DropdownMenuItem className="flex cursor-pointer items-center gap-2">
                  <Gamepad2 className="h-4 w-4" />
                  <a href="/profile/collections">My Collections</a>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-zinc-800" />
                <DropdownMenuItem
                  onClick={() => signOut()}
                  className="flex cursor-pointer items-center gap-2 text-red-400 focus:text-red-400"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Sign Out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Link href="/login">
              <Button
                size="sm"
                className="rounded-full bg-purple-600 text-xs hover:bg-purple-700"
              >
                Sign In
              </Button>
            </Link>
          )}

          {/* Mobile menu toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="text-zinc-400 md:hidden"
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="border-t border-zinc-800 bg-black px-4 pb-4 pt-2 md:hidden">
          <form onSubmit={handleSearch} className="relative mb-4">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
            <Input
              type="search"
              placeholder="Search games & mods..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-10 w-full rounded-full border-zinc-700 bg-zinc-900 pl-9 text-sm text-zinc-300 placeholder:text-zinc-500"
            />
          </form>
          <div className="flex flex-col gap-2">
            <Link
              href="/games"
              className="rounded-lg px-3 py-2 text-sm font-medium text-zinc-400 transition-colors hover:bg-zinc-900 hover:text-white"
              onClick={() => setMobileMenuOpen(false)}
            >
              Game Library
            </Link>
            <Link
              href="/games?featured=true"
              className="rounded-lg px-3 py-2 text-sm font-medium text-zinc-400 transition-colors hover:bg-zinc-900 hover:text-white"
              onClick={() => setMobileMenuOpen(false)}
            >
              Featured Mods
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
