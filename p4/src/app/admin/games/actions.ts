"use server";

import { revalidatePath } from "next/cache";
import { prisma } from "@/lib/prisma";
import { auth } from "@/lib/auth";

async function requireAdmin(): Promise<void> {
  const session = await auth();
  if (!session?.user?.id) throw new Error("Unauthorized");

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    select: { role: true },
  });

  if (user?.role !== "ADMIN") throw new Error("Forbidden");
}

export async function toggleGameFeatured(formData: FormData) {
  await requireAdmin();

  const gameId = formData.get("gameId") as string;
  const featured = formData.get("featured") as string;

  if (!gameId || !featured) throw new Error("Invalid input");

  await prisma.game.update({
    where: { id: gameId },
    data: { featured: featured === "true" },
  });

  revalidatePath("/admin/games");
}
