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

export async function updateUserRole(formData: FormData) {
  await requireAdmin();

  const userId = formData.get("userId") as string;
  const role = formData.get("role") as string;

  if (!userId || !["USER", "MODDER"].includes(role)) {
    throw new Error("Invalid input");
  }

  // Prevent removing the last admin
  const targetUser = await prisma.user.findUnique({
    where: { id: userId },
    select: { role: true },
  });

  if (!targetUser) throw new Error("User not found");
  if (targetUser.role === "ADMIN") throw new Error("Cannot modify admin users");

  await prisma.user.update({
    where: { id: userId },
    data: { role: role as any },
  });

  revalidatePath("/admin/users");
}
