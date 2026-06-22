"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Sword,
  MessagesSquare,
  User,
  ArrowRight,
  Shield,
  ChevronDown,
  ChevronUp,
  Mail,
  Lock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const router = useRouter();
  const [guestName, setGuestName] = useState("");
  const [loading, setLoading] = useState<string | null>(null);
  const [showAdmin, setShowAdmin] = useState(false);
  const [adminEmail, setAdminEmail] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [adminError, setAdminError] = useState("");

  const handleDiscordLogin = async () => {
    setLoading("discord");
    await signIn("discord", { callbackUrl: "/games" });
  };

  const handleGuestLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!guestName.trim()) return;
    setLoading("guest");
    await signIn("guest", {
      name: guestName.trim(),
      callbackUrl: "/games",
    });
  };

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!adminEmail.trim() || !adminPassword.trim()) return;
    setLoading("admin");
    setAdminError("");

    const result = await signIn("admin", {
      email: adminEmail.trim(),
      password: adminPassword,
      redirect: false,
    });

    if (result?.error) {
      setAdminError("Invalid email or password. Please try again.");
      setLoading(null);
    } else {
      router.push("/profile");
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-blue-600">
            <Sword className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">Welcome to ModHub</h1>
          <p className="mt-2 text-zinc-400">
            Sign in to browse, download, and manage mods
          </p>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
          {/* Admin Login Toggle */}
          <button
            onClick={() => setShowAdmin(!showAdmin)}
            className="mb-4 flex w-full items-center justify-between rounded-lg border border-zinc-700 bg-zinc-800/50 px-4 py-3 text-sm text-zinc-300 transition-colors hover:bg-zinc-800"
          >
            <span className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-purple-400" />
              Admin Sign In
            </span>
            {showAdmin ? (
              <ChevronUp className="h-4 w-4 text-zinc-500" />
            ) : (
              <ChevronDown className="h-4 w-4 text-zinc-500" />
            )}
          </button>

          {/* Admin Login Form */}
          {showAdmin && (
            <form onSubmit={handleAdminLogin} className="mb-6 space-y-3">
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
                <Input
                  type="email"
                  placeholder="Admin email"
                  value={adminEmail}
                  onChange={(e) => setAdminEmail(e.target.value)}
                  className="h-11 w-full rounded-lg border-zinc-700 bg-zinc-800 pl-10 text-sm text-zinc-300 placeholder:text-zinc-500 focus:border-purple-500"
                  autoComplete="email"
                />
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
                <Input
                  type="password"
                  placeholder="Password"
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                  className="h-11 w-full rounded-lg border-zinc-700 bg-zinc-800 pl-10 text-sm text-zinc-300 placeholder:text-zinc-500 focus:border-purple-500"
                  autoComplete="current-password"
                />
              </div>
              {adminError && (
                <p className="text-xs text-red-400">{adminError}</p>
              )}
              <Button
                type="submit"
                disabled={
                  loading !== null || !adminEmail.trim() || !adminPassword.trim()
                }
                className="h-11 w-full rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-base font-medium hover:from-purple-700 hover:to-blue-700 disabled:opacity-50"
              >
                {loading === "admin" ? (
                  "Signing in..."
                ) : (
                  <>
                    Sign In as Admin
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </form>
          )}

          {/* Discord Login */}
          <Button
            onClick={handleDiscordLogin}
            disabled={loading !== null}
            className="mb-4 flex h-12 w-full items-center justify-center gap-3 rounded-lg bg-[#5865F2] text-base font-medium text-white hover:bg-[#4752c4]"
          >
            <MessagesSquare className="h-5 w-5" />
            {loading === "discord" ? "Connecting..." : "Continue with Discord"}
          </Button>

          <div className="relative mb-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-zinc-800" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-zinc-900 px-2 text-zinc-600">
                or continue as guest
              </span>
            </div>
          </div>

          {/* Guest Login */}
          <form onSubmit={handleGuestLogin} className="space-y-3">
            <div className="relative">
              <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
              <Input
                type="text"
                placeholder="Enter a display name"
                value={guestName}
                onChange={(e) => setGuestName(e.target.value)}
                className="h-11 w-full rounded-lg border-zinc-700 bg-zinc-800 pl-10 text-sm text-zinc-300 placeholder:text-zinc-500 focus:border-purple-500"
                maxLength={30}
              />
            </div>
            <Button
              type="submit"
              disabled={loading !== null || !guestName.trim()}
              className="h-11 w-full rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-base font-medium hover:from-purple-700 hover:to-blue-700 disabled:opacity-50"
            >
              {loading === "guest" ? (
                "Signing in..."
              ) : (
                <>
                  Continue as Guest
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </form>
        </div>

        <p className="mt-4 text-center text-xs text-zinc-600">
          By continuing, you agree to our Terms of Service and Privacy Policy.
          ModHub is for single-player games only.
        </p>
      </div>
    </div>
  );
}
