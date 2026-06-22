import { redirect } from "next/navigation";
import Link from "next/link";
import { auth } from "@/lib/auth";
import {
  LayoutDashboard,
  Gamepad2,
  Puzzle,
  Users,
  ArrowLeft,
} from "lucide-react";

const sidebarLinks = [
  {
    label: "Overview",
    href: "/admin",
    icon: LayoutDashboard,
  },
  {
    label: "Games",
    href: "/admin/games",
    icon: Gamepad2,
  },
  {
    label: "Mods",
    href: "/admin/mods",
    icon: Puzzle,
  },
  {
    label: "Users",
    href: "/admin/users",
    icon: Users,
  },
];

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();
  if (!session?.user?.id) redirect("/login");

  if (session.user.role !== "ADMIN") {
    redirect("/");
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <aside className="hidden w-64 flex-shrink-0 border-r border-zinc-800 bg-zinc-900/50 lg:block">
        <nav className="sticky top-16 space-y-1 p-4">
          {sidebarLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-white"
            >
              <link.icon className="h-4 w-4" />
              {link.label}
            </Link>
          ))}
          <div className="pt-4">
            <Link
              href="/"
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-zinc-600 transition-colors hover:text-zinc-400"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Site
            </Link>
          </div>
        </nav>
      </aside>

      {/* Mobile nav */}
      <nav className="flex gap-1 border-b border-zinc-800 bg-zinc-900/50 px-4 py-2 lg:hidden">
        {sidebarLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-white"
          >
            <link.icon className="h-3.5 w-3.5" />
            {link.label}
          </Link>
        ))}
      </nav>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  );
}
