import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { SessionProvider } from "@/components/SessionProvider";
import { Toaster } from "@/components/ui/sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ModHub - Game Mods & Trainers",
  description:
    "Discover the best mods and trainers for your favorite games. Browse, download, and manage your mod collection.",
  keywords: ["game mods", "trainers", "gaming", "mods", "pc gaming"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="flex min-h-full flex-col bg-black text-zinc-100">
        <SessionProvider>
          <Navbar />
          <main className="flex-1">{children}</main>
          <Toaster />
        </SessionProvider>
      </body>
    </html>
  );
}
