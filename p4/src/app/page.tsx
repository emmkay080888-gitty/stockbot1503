import Link from "next/link";
import { ArrowRight, Gamepad2, Download, Users, Star, Shield, Zap, Sword } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-zinc-800">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-purple-950/40 via-black to-black" />
        <div className="absolute left-1/2 top-0 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-purple-600/10 blur-3xl" />

        <div className="relative mx-auto max-w-7xl px-4 pb-20 pt-16 sm:px-6 sm:pb-28 sm:pt-24">
          <div className="flex flex-col items-center text-center">
            {/* Badge */}
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-purple-500/20 bg-purple-500/10 px-4 py-1.5 text-sm text-purple-300">
              <Zap className="h-3.5 w-3.5" />
              The ultimate game modding platform
            </div>

            <h1 className="max-w-4xl text-4xl font-bold tracking-tight text-white sm:text-6xl lg:text-7xl">
              Level Up Your
              <span className="bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
                {" "}Gaming Experience
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-zinc-400">
              Discover thousands of community-created mods and trainers for your
              favorite games. One-click downloads, verified content, and a
              thriving community of modders.
            </p>

            <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
              <Link href="/games">
                <Button className="h-12 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 px-8 text-base font-medium text-white hover:from-purple-700 hover:to-blue-700">
                  Browse Game Library
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/games?featured=true">
                <Button
                  variant="outline"
                  className="h-12 rounded-full border-zinc-700 px-8 text-base font-medium text-zinc-300 hover:bg-zinc-900 hover:text-white"
                >
                  Explore Featured Mods
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="border-b border-zinc-800 bg-zinc-900/50">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {[
              { icon: Gamepad2, label: "Games Supported", value: "500+" },
              { icon: Download, label: "Total Mod Downloads", value: "2.4M+" },
              { icon: Users, label: "Active Users", value: "50K+" },
              { icon: Star, label: "Community Rating", value: "4.8/5" },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10">
                  <stat.icon className="h-6 w-6 text-purple-400" />
                </div>
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <div className="mt-1 text-sm text-zinc-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            Why ModHub?
          </h2>
          <p className="mt-4 text-lg text-zinc-400">
            Everything you need to transform your gaming experience
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {[
            {
              icon: Shield,
              title: "Verified & Safe",
              description:
                "All mods are community-tested and verified safe. No malware, no viruses — just pure gaming enhancements.",
              gradient: "from-purple-500/20 to-purple-600/5",
            },
            {
              icon: Zap,
              title: "One-Click Install",
              description:
                "No more hunting through forums. Browse, click, and play. Our platform handles everything else.",
              gradient: "from-blue-500/20 to-blue-600/5",
            },
            {
              icon: Gamepad2,
              title: "Auto Game Detection",
              description:
                "ModHub automatically detects your installed games and shows you compatible mods and trainers instantly.",
              gradient: "from-cyan-500/20 to-cyan-600/5",
            },
            {
              icon: Users,
              title: "Community Driven",
              description:
                "Join thousands of modders and gamers. Share collections, rate mods, and contribute to the community.",
              gradient: "from-emerald-500/20 to-emerald-600/5",
            },
            {
              icon: Star,
              title: "Curated Collections",
              description:
                "Discover hand-picked mod collections optimized for the best experience. Save and share your own.",
              gradient: "from-yellow-500/20 to-yellow-600/5",
            },
            {
              icon: Sword,
              title: "Trainers & Cheats",
              description:
                "Unlock new ways to play with built-in trainers. Infinite health, ammo, and more at your fingertips.",
              gradient: "from-red-500/20 to-red-600/5",
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className={`group rounded-xl border border-zinc-800 bg-gradient-to-br ${feature.gradient} p-6 transition-all duration-300 hover:border-zinc-700 hover:shadow-lg`}
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-800">
                <feature.icon className="h-5 w-5 text-purple-400" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-white">
                {feature.title}
              </h3>
              <p className="text-sm leading-6 text-zinc-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t border-zinc-800 bg-gradient-to-b from-zinc-900 to-black">
        <div className="mx-auto max-w-7xl px-4 py-20 text-center sm:px-6">
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            Ready to transform your games?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-zinc-400">
            Join the community and start exploring thousands of mods and trainers
            for your favorite games.
          </p>
          <Link href="/games">
            <Button className="mt-8 h-12 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 px-8 text-base font-medium hover:from-purple-700 hover:to-blue-700">
              Get Started Now
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800 py-8">
        <div className="mx-auto max-w-7xl px-4 text-center text-sm text-zinc-600 sm:px-6">
          <p>ModHub — Built for gamers, by gamers. Single-player only.</p>
        </div>
      </footer>
    </div>
  );
}
