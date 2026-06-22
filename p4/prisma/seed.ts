import { PrismaClient } from "../src/generated/prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import { Platform, ModType, ModStatus } from "../src/generated/prisma/enums";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error("DATABASE_URL is not set");
}
const adapter = new PrismaPg(connectionString);
const prisma = new PrismaClient({ adapter });

const genres = [
  { name: "Action", slug: "action" },
  { name: "Adventure", slug: "adventure" },
  { name: "RPG", slug: "rpg" },
  { name: "Strategy", slug: "strategy" },
  { name: "Simulation", slug: "simulation" },
  { name: "Sports", slug: "sports" },
  { name: "Racing", slug: "racing" },
  { name: "FPS", slug: "fps" },
  { name: "Open World", slug: "open-world" },
  { name: "Horror", slug: "horror" },
  { name: "Puzzle", slug: "puzzle" },
  { name: "Fighting", slug: "fighting" },
];

const tags = [
  { name: "Graphics", slug: "graphics" },
  { name: "Gameplay", slug: "gameplay" },
  { name: "UI", slug: "ui" },
  { name: "Cheats", slug: "cheats" },
  { name: "Performance", slug: "performance" },
  { name: "Quality of Life", slug: "quality-of-life" },
  { name: "Overlay", slug: "overlay" },
  { name: "Bug Fix", slug: "bug-fix" },
  { name: "Content", slug: "content" },
  { name: "Multiplayer", slug: "multiplayer" },
];

const games = [
  {
    title: "Cyberpunk 2077",
    slug: "cyberpunk-2077",
    description:
      "Cyberpunk 2077 is an open-world, action-adventure RPG set in the megalopolis of Night City, where you play as a mercenary outlaw wrapped up in a life-or-death struggle. Explore the dark future of the cyberpunk genre and discover a world filled with advanced tech, deadly weapons, and high-stakes intrigue.",
    shortDescription: "Open-world action RPG in Night City",
    developer: "CD Projekt Red",
    publisher: "CD Projekt",
    releaseDate: new Date("2020-12-10"),
    platforms: [Platform.PC, Platform.XBOX, Platform.PLAYSTATION],
    featured: true,
    genres: ["action", "rpg", "open-world"],
    coverImage: null,
    bannerImage: null,
  },
  {
    title: "Elden Ring",
    slug: "elden-ring",
    description:
      "Elden Ring is an action RPG developed by FromSoftware and published by Bandai Namco Entertainment. The game is set in the Lands Between, a vast world filled with dungeons, bosses, and secrets. Rise, Tarnished, and become the Elden Lord.",
    shortDescription: "Action RPG in the Lands Between",
    developer: "FromSoftware",
    publisher: "Bandai Namco",
    releaseDate: new Date("2022-02-25"),
    platforms: [Platform.PC, Platform.XBOX, Platform.PLAYSTATION],
    featured: true,
    genres: ["action", "rpg", "adventure"],
    coverImage: null,
    bannerImage: null,
  },
  {
    title: "Baldur's Gate 3",
    slug: "baldurs-gate-3",
    description:
      "Baldur's Gate 3 is a role-playing video game developed and published by Larian Studios. It is the third main game in the Baldur's Gate series, based on the Dungeons & Dragons tabletop role-playing system. Gather your party and return to the Forgotten Realms.",
    shortDescription: "Epic D&D-based RPG",
    developer: "Larian Studios",
    publisher: "Larian Studios",
    releaseDate: new Date("2023-08-03"),
    platforms: [Platform.PC, Platform.PLAYSTATION, Platform.XBOX],
    featured: true,
    genres: ["rpg", "adventure", "strategy"],
    coverImage: null,
    bannerImage: null,
  },
  {
    title: "Grand Theft Auto V",
    slug: "gta-v",
    description:
      "Grand Theft Auto V is an action-adventure game developed by Rockstar North and published by Rockstar Games. It is the seventh main installment in the Grand Theft Auto series, set in the sprawling city of Los Santos and its surrounding areas.",
    shortDescription: "Open-world crime epic",
    developer: "Rockstar North",
    publisher: "Rockstar Games",
    releaseDate: new Date("2013-09-17"),
    platforms: [Platform.PC, Platform.XBOX, Platform.PLAYSTATION],
    featured: true,
    genres: ["action", "open-world", "adventure"],
    coverImage: null,
    bannerImage: null,
  },
  {
    title: "Red Dead Redemption 2",
    slug: "red-dead-redemption-2",
    description:
      "Red Dead Redemption 2 is an action-adventure game developed and published by Rockstar Games. Set in 1899 in a fictionalized representation of the American West, the story follows outlaw Arthur Morgan and the Van der Linde gang.",
    shortDescription: "Wild West action-adventure",
    developer: "Rockstar Games",
    publisher: "Rockstar Games",
    releaseDate: new Date("2018-10-26"),
    platforms: [Platform.PC, Platform.XBOX, Platform.PLAYSTATION],
    featured: false,
    genres: ["action", "adventure", "open-world"],
    coverImage: null,
    bannerImage: null,
  },
  {
    title: "The Witcher 3: Wild Hunt",
    slug: "the-witcher-3",
    description:
      "The Witcher 3: Wild Hunt is an action RPG set in a vast open world. Play as Geralt of Rivia, a monster hunter for hire, and embark on an epic journey to find your adopted daughter and stop the otherworldly Wild Hunt.",
    shortDescription: "Open-world monster hunting RPG",
    developer: "CD Projekt Red",
    publisher: "CD Projekt",
    releaseDate: new Date("2015-05-19"),
    platforms: [Platform.PC, Platform.XBOX, Platform.PLAYSTATION, Platform.NINTENDO],
    featured: false,
    genres: ["action", "rpg", "open-world"],
    coverImage: null,
    bannerImage: null,
  },
  {
    title: "Stardew Valley",
    slug: "stardew-valley",
    description:
      "Stardew Valley is a simulation RPG developed by Eric Barone. You inherit your grandfather's old farm in Stardew Valley and must manage crops, animals, and relationships while exploring caves and restoring the community center.",
    shortDescription: "Farming and life simulation RPG",
    developer: "Eric Barone",
    publisher: "ConcernedApe",
    releaseDate: new Date("2016-02-26"),
    platforms: [Platform.PC, Platform.XBOX, Platform.PLAYSTATION, Platform.NINTENDO, Platform.MOBILE],
    featured: false,
    genres: ["simulation", "rpg"],
    coverImage: null,
    bannerImage: null,
  },
  {
    title: "Counter-Strike 2",
    slug: "counter-strike-2",
    description:
      "Counter-Strike 2 is a multiplayer first-person shooter game developed by Valve. It is the successor to Counter-Strike: Global Offensive and features improved graphics, physics, and gameplay mechanics.",
    shortDescription: "Tactical FPS",
    developer: "Valve",
    publisher: "Valve",
    releaseDate: new Date("2023-09-27"),
    platforms: [Platform.PC],
    featured: false,
    genres: ["fps", "action"],
    coverImage: null,
    bannerImage: null,
  },
  {
    title: "Factorio",
    slug: "factorio",
    description:
      "Factorio is a game about building and creating automated factories. You mine resources, research technologies, build infrastructure, automate production, and fight enemies. Explore a vast world and build ever more complex factories.",
    shortDescription: "Factory automation sim",
    developer: "Wube Software",
    publisher: "Wube Software",
    releaseDate: new Date("2020-08-14"),
    platforms: [Platform.PC],
    featured: false,
    genres: ["simulation", "strategy"],
    coverImage: null,
    bannerImage: null,
  },
  {
    title: "Resident Evil 4 Remake",
    slug: "resident-evil-4-remake",
    description:
      "Survival is just the beginning. Six years have passed since the biological disaster in Raccoon City. Agent Leon S. Kennedy, one of the survivors, tracks the president's kidnapped daughter to a secluded European village.",
    shortDescription: "Survival horror remake",
    developer: "Capcom",
    publisher: "Capcom",
    releaseDate: new Date("2023-03-24"),
    platforms: [Platform.PC, Platform.XBOX, Platform.PLAYSTATION],
    featured: false,
    genres: ["horror", "action", "adventure"],
    coverImage: null,
    bannerImage: null,
  },
];

const modTemplates = [
  {
    title: "Ultimate Graphics Overhaul",
    slug: "ultimate-graphics-overhaul",
    description:
      "Completely transforms the visual experience with enhanced textures, improved lighting, and advanced post-processing effects. This mod pushes the graphical capabilities to the limit while maintaining stable performance. Features include:\n\n- 4K texture packs for all environments\n- Ray tracing improvements and optimizations\n- Enhanced particle effects and weather systems\n- Custom color grading and LUTs\n- Improved draw distances and LOD settings",
    shortDescription: "Complete graphical enhancement pack",
    type: "QOL" as const,
    downloads: 45231,
    views: 124500,
    likes: 3200,
    verified: true,
    featured: true,
    tags: ["graphics", "performance"],
  },
  {
    title: "Trainer - Infinite Resources",
    slug: "trainer-infinite-resources",
    description:
      "A comprehensive trainer that gives you access to unlimited resources, health, and ammunition. Perfect for players who want to explore the game without limitations or experiment with different playstyles.",
    shortDescription: "Unlimited health, ammo, and resources",
    type: "TRAINER" as const,
    downloads: 89200,
    views: 245000,
    likes: 5600,
    verified: true,
    featured: true,
    tags: ["cheats", "gameplay"],
  },
  {
    title: "Immersive UI Redesign",
    slug: "immersive-ui-redesign",
    description:
      "A complete overhaul of the user interface designed to be more immersive and less intrusive. Cleans up cluttered HUD elements while keeping important information accessible through elegant animations and smart visibility toggles.",
    shortDescription: "Clean, modern UI overhaul",
    type: "UI" as const,
    downloads: 18300,
    views: 45200,
    likes: 1800,
    verified: true,
    featured: false,
    tags: ["ui", "quality-of-life"],
  },
  {
    title: "Performance Optimization Pack",
    slug: "performance-optimization-pack",
    description:
      "Maximize your framerate with this comprehensive performance optimization mod. Tweaks engine settings, optimizes shaders, and reduces unnecessary background processes for a smoother gaming experience.",
    shortDescription: "Boost FPS and reduce stuttering",
    type: "FIX" as const,
    downloads: 67100,
    views: 156000,
    likes: 4100,
    verified: true,
    featured: true,
    tags: ["performance", "bug-fix"],
  },
  {
    title: "Expanded Content Pack",
    slug: "expanded-content-pack",
    description:
      "Adds new weapons, items, enemies, and side quests to the game. This content expansion has been carefully balanced to fit seamlessly into the existing game world while providing fresh challenges and rewards.",
    shortDescription: "New weapons, items, and quests",
    type: "CONTENT" as const,
    downloads: 28400,
    views: 72300,
    likes: 2200,
    verified: false,
    featured: false,
    tags: ["content", "gameplay"],
  },
  {
    title: "In-Game Overlay - Stats & Map",
    slug: "overlay-stats-and-map",
    description:
      "A feature-rich overlay that provides real-time statistics, an interactive minimap, and performance monitoring. Accessible with a single hotkey, this overlay enhances your gameplay without interrupting it.",
    shortDescription: "Real-time stats and minimap overlay",
    type: "OVERLAY" as const,
    downloads: 34200,
    views: 87600,
    likes: 2900,
    verified: true,
    featured: false,
    tags: ["overlay", "ui", "gameplay"],
  },
];

async function main() {
  console.log("Seeding database...");

  // Clean existing data
  await prisma.userFavorite.deleteMany();
  await prisma.modReview.deleteMany();
  await prisma.gameReview.deleteMany();
  await prisma.collectionEntry.deleteMany();
  await prisma.collection.deleteMany();
  await prisma.tagOnMod.deleteMany();
  await prisma.tag.deleteMany();
  await prisma.genreOnGame.deleteMany();
  await prisma.genre.deleteMany();
  await prisma.mod.deleteMany();
  await prisma.game.deleteMany();
  await prisma.user.deleteMany();
  await prisma.session.deleteMany();
  await prisma.account.deleteMany();
  await prisma.verificationToken.deleteMany();

  // Create tags
  const createdTags = await Promise.all(
    tags.map((tag) => prisma.tag.create({ data: tag }))
  );
  console.log(`Created ${createdTags.length} tags`);

  // Create genres
  const createdGenres = await Promise.all(
    genres.map((genre) => prisma.genre.create({ data: genre }))
  );
  console.log(`Created ${createdGenres.length} genres`);

  const tagMap = Object.fromEntries(
    createdTags.map((t) => [t.slug, t.id])
  );
  const genreMap = Object.fromEntries(
    createdGenres.map((g) => [g.slug, g.id])
  );

  // Create admin user
  const admin = await prisma.user.create({
    data: {
      name: "ModHub Admin",
      email: "admin@modhub.dev",
      role: "ADMIN",
      bio: "Platform administrator and mod curator.",
    },
  });
  console.log("Created admin user");

  // Create games
  for (const gameData of games) {
    const { genres: genreSlugs, ...gameFields } = gameData;

    const game = await prisma.game.create({
      data: {
        ...gameFields,
        genres: {
          create: genreSlugs.map((slug) => ({
            genre: { connect: { id: genreMap[slug] } },
          })),
        },
      },
    });

    // Create mods for each game
    const modCount = Math.floor(Math.random() * modTemplates.length) + 1;
    const selectedMods = modTemplates
      .sort(() => Math.random() - 0.5)
      .slice(0, modCount);

    for (let i = 0; i < selectedMods.length; i++) {
      const modTemplate = selectedMods[i];
      const uniqueSlug = `${game.slug}-${modTemplate.slug}`;
      const mod = await prisma.mod.create({
        data: {
          ...modTemplate,
          slug: uniqueSlug,
          gameId: game.id,
          authorId: admin.id,
          status: "APPROVED",
          images: [],
          tags: {
            create: modTemplate.tags.map((slug) => ({
              tag: { connect: { id: tagMap[slug] } },
            })),
          },
        },
      });
    }

    // Update game mod count
    await prisma.game.update({
      where: { id: game.id },
      data: { modCount: selectedMods.length },
    });
  }

  // Create a demo collection
  const collection = await prisma.collection.create({
    data: {
      name: "Best Graphics Mods",
      description:
        "A curated collection of the best graphical enhancement mods for an incredible visual experience.",
      isPublic: true,
      userId: admin.id,
    },
  });

  console.log("Created sample collection");
  console.log("Database seeded successfully!");
}

main()
  .catch((e) => {
    console.error("Error seeding database:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
