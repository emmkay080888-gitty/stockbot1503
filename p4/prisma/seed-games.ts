import "dotenv/config";
import { PrismaClient } from "../src/generated/prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import { Platform, ModType } from "../src/generated/prisma/enums";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error("DATABASE_URL is not set");
}
const adapter = new PrismaPg(connectionString);
const prisma = new PrismaClient({ adapter });

async function main() {
  console.log("Adding 007 First Light and Black Myth: Wukong...\n");

  // Find or create genres
  const genres = await prisma.genre.findMany();
  const genreMap = Object.fromEntries(genres.map((g) => [g.slug, g.id]));

  // Find or create tags
  const tagMap: Record<string, string> = {};
  const tagSlugs = [
    "graphics", "gameplay", "ui", "cheats", "performance",
    "quality-of-life", "overlay", "bug-fix", "content", "multiplayer",
  ];
  for (const slug of tagSlugs) {
    const tag = await prisma.tag.findUnique({ where: { slug } });
    if (tag) tagMap[slug] = tag.id;
  }

  // Find or create admin user
  let admin = await prisma.user.findUnique({ where: { email: "admin@modhub.dev" } });
  if (!admin) {
    admin = await prisma.user.create({
      data: {
        name: "ModHub Admin",
        email: "admin@modhub.dev",
        role: "ADMIN",
        bio: "Platform administrator and mod curator.",
      },
    });
  }

  // ========================================
  // 007 First Light
  // ========================================
  const jamesBondGame = await prisma.game.upsert({
    where: { slug: "007-first-light" },
    update: {},
    create: {
      title: "007 First Light",
      slug: "007-first-light",
      description:
        "007 First Light is an action-adventure game developed by IO Interactive that serves as a standalone origin story for James Bond. Set in a world of international espionage, the game follows a young, reckless Bond as he undergoes grueling MI6 training and uncovers a conspiracy involving artificial intelligence. Players traverse stunning international locations including Iceland, Malta, Slovakia, Mauritania, London, Vietnam, and Antarctica, utilizing cutting-edge gadgets and stealth mechanics.",
      shortDescription: "James Bond origin story from the makers of Hitman",
      developer: "IO Interactive",
      publisher: "IO Interactive",
      releaseDate: new Date("2026-05-27"),
      platforms: [Platform.PC, Platform.XBOX, Platform.PLAYSTATION],
      featured: true,
      averageRating: 4.7,
      genres: {
        create: [
          { genre: { connect: { id: genreMap["action"] } } },
          { genre: { connect: { id: genreMap["adventure"] } } },
        ],
      },
    },
  });

  const bondMods: Array<{
    title: string; slug: string; description: string; shortDescription: string;
    type: "QOL" | "CONTENT" | "FIX" | "TRAINER";
    downloads: number; views: number; likes: number;
    verified: boolean; featured: boolean; tags: string[];
  }> = [
    {
      title: "Enhanced Stealth AI",
      slug: "007-first-light-enhanced-stealth-ai",
      description:
        "Overhauls the enemy AI to provide a more realistic and challenging stealth experience. Guards now coordinate searches, investigate disturbances more intelligently, and react dynamically to your actions.",
      shortDescription: "Smarter and more realistic enemy AI",
      type: "QOL",
      downloads: 12300,
      views: 45200,
      likes: 890,
      verified: true,
      featured: true,
      tags: ["gameplay", "quality-of-life"],
    },
    {
      title: "Classic Bond Gadget Pack",
      slug: "007-first-light-classic-gadgets",
      description:
        "Adds a collection of iconic James Bond gadgets from the classic film era. Includes the Walther PPK with silencer, wrist-mounted dart gun, explosive pen, and the iconic jetpack.",
      shortDescription: "Iconic gadgets from classic Bond films",
      type: "CONTENT",
      downloads: 8900,
      views: 32100,
      likes: 720,
      verified: true,
      featured: true,
      tags: ["content", "gameplay"],
    },
    {
      title: "Glacier Engine Graphics Tweak",
      slug: "007-first-light-graphics-tweak",
      description:
        "Optimizes the Glacier 2 engine for better performance on a wider range of hardware. Includes custom DLSS profiles, improved shadow cascades, and optimized ambient occlusion.",
      shortDescription: "Performance optimization and visual tweaks",
      type: "FIX",
      downloads: 18400,
      views: 56300,
      likes: 1200,
      verified: true,
      featured: false,
      tags: ["performance", "graphics"],
    },
    {
      title: "Trainer - All Gadgets Unlocked",
      slug: "007-first-light-trainer-all-gadgets",
      description:
        "Unlocks all gadgets and upgrades from the start of the game. Includes infinite ammo for special weapons, no cooldown on gadget usage, and enhanced movement capabilities.",
      shortDescription: "Unlock all gadgets and upgrades",
      type: "TRAINER",
      downloads: 32100,
      views: 98700,
      likes: 2100,
      verified: true,
      featured: true,
      tags: ["cheats", "gameplay"],
    },
  ];

  for (const mod of bondMods) {
    await prisma.mod.upsert({
      where: { slug: mod.slug },
      update: {},
      create: {
        title: mod.title,
        slug: mod.slug,
        description: mod.description,
        shortDescription: mod.shortDescription,
        type: mod.type as unknown as any,
        version: "1.0.0",
        downloads: mod.downloads,
        views: mod.views,
        likes: mod.likes,
        verified: mod.verified,
        featured: mod.featured,
        status: "APPROVED",
        gameId: jamesBondGame.id,
        authorId: admin.id,
        images: [],
        tags: {
          create: mod.tags.map((slug) => ({
            tag: { connect: { id: tagMap[slug] } },
          })),
        },
      },
    });
  }

  await prisma.game.update({
    where: { id: jamesBondGame.id },
    data: { modCount: bondMods.length },
  });
  console.log(`✅ 007 First Light — added ${bondMods.length} mods`);

  // ========================================
  // Black Myth: Wukong
  // ========================================
  const wukongGame = await prisma.game.upsert({
    where: { slug: "black-myth-wukong" },
    update: {},
    create: {
      title: "Black Myth: Wukong",
      slug: "black-myth-wukong",
      description:
        "Black Myth: Wukong is an action RPG developed by Game Science, inspired by the classic 16th-century Chinese novel Journey to the West. Built on Unreal Engine 5, the game features stunning visuals, deep combat with multiple staff stances and spells, and epic boss battles against legendary foes from Chinese mythology.",
      shortDescription: "Epic action RPG rooted in Chinese mythology",
      developer: "Game Science",
      publisher: "Game Science",
      releaseDate: new Date("2024-08-20"),
      platforms: [Platform.PC, Platform.XBOX, Platform.PLAYSTATION],
      featured: true,
      averageRating: 4.9,
      genres: {
        create: [
          { genre: { connect: { id: genreMap["action"] } } },
          { genre: { connect: { id: genreMap["rpg"] } } },
          { genre: { connect: { id: genreMap["adventure"] } } },
        ],
      },
    },
  });

  const wukongMods: Array<{
    title: string; slug: string; description: string; shortDescription: string;
    type: "QOL" | "CONTENT" | "TRAINER" | "FIX" | "UI";
    downloads: number; views: number; likes: number;
    verified: boolean; featured: boolean; tags: string[];
  }> = [
    {
      title: "Ultimate Graphics Overhaul",
      slug: "black-myth-wukong-ultimate-graphics",
      description:
        "Pushes Unreal Engine 5 to its absolute limits with enhanced Lumen reflections, improved Nanite geometry pools, custom ray-traced global illumination, and 8K-ready texture packs.",
      shortDescription: "Ultimate UE5 visual enhancement pack",
      type: "QOL",
      downloads: 67300,
      views: 189000,
      likes: 5400,
      verified: true,
      featured: true,
      tags: ["graphics", "performance"],
    },
    {
      title: "New Game Plus+ Expansion",
      slug: "black-myth-wukong-ng-plus",
      description:
        "A comprehensive New Game Plus expansion that adds new enemies, boss variants, secret areas, and an extended ending.",
      shortDescription: "New bosses, skills, and extended ending",
      type: "CONTENT",
      downloads: 45200,
      views: 134000,
      likes: 3800,
      verified: true,
      featured: true,
      tags: ["content", "gameplay"],
    },
    {
      title: "Trainer - Immortal Wukong",
      slug: "black-myth-wukong-immortal-trainer",
      description:
        "Unlock the full power of the Destined One with this comprehensive trainer. Features include infinite health and stamina, unlimited mana, no cooldowns on spells, one-hit kill mode.",
      shortDescription: "Infinite health, mana, one-hit kills",
      type: "TRAINER",
      downloads: 89100,
      views: 256000,
      likes: 7200,
      verified: true,
      featured: true,
      tags: ["cheats", "gameplay"],
    },
    {
      title: "Staff Moveset Expansion",
      slug: "black-myth-wukong-staff-expansion",
      description:
        "Expands the combat system with 8 new staff stances, 15 new combos, and unique weapon arts.",
      shortDescription: "New staff stances and combat moves",
      type: "CONTENT",
      downloads: 34100,
      views: 89200,
      likes: 2900,
      verified: true,
      featured: false,
      tags: ["gameplay", "content"],
    },
    {
      title: "Performance Optimization",
      slug: "black-myth-wukong-performance",
      description:
        "Optimizes engine settings for smoother performance on mid-range hardware. Includes optimized shader compilation, reduced stutter, improved VRAM management.",
      shortDescription: "Boost FPS on mid-range PCs",
      type: "FIX",
      downloads: 78400,
      views: 201000,
      likes: 6100,
      verified: true,
      featured: false,
      tags: ["performance", "bug-fix"],
    },
    {
      title: "UI Overhaul - Mythic Interface",
      slug: "black-myth-wukong-ui-overhaul",
      description:
        "A complete redesign of the user interface inspired by traditional Chinese ink wash painting aesthetics.",
      shortDescription: "Beautiful Chinese ink wash UI redesign",
      type: "UI",
      downloads: 22100,
      views: 56700,
      likes: 1800,
      verified: true,
      featured: false,
      tags: ["ui", "quality-of-life"],
    },
  ];

  for (const mod of wukongMods) {
    await prisma.mod.upsert({
      where: { slug: mod.slug },
      update: {},
      create: {
        title: mod.title,
        slug: mod.slug,
        description: mod.description,
        shortDescription: mod.shortDescription,
        type: mod.type as unknown as any,
        version: "1.0.0",
        downloads: mod.downloads,
        views: mod.views,
        likes: mod.likes,
        verified: mod.verified,
        featured: mod.featured,
        status: "APPROVED",
        gameId: wukongGame.id,
        authorId: admin.id,
        images: [],
        tags: {
          create: mod.tags.map((slug) => ({
            tag: { connect: { id: tagMap[slug] } },
          })),
        },
      },
    });
  }

  await prisma.game.update({
    where: { id: wukongGame.id },
    data: { modCount: wukongMods.length },
  });
  console.log(`✅ Black Myth: Wukong — added ${wukongMods.length} mods`);

  console.log("\n🎉 Done! Both games and their mods have been added.");
}

main()
  .catch((e) => {
    console.error("Error:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
