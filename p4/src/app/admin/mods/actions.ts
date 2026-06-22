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

export async function updateModStatus(formData: FormData) {
  await requireAdmin();

  const modId = formData.get("modId") as string;
  const status = formData.get("status") as string;

  if (!modId || !["PENDING", "APPROVED", "REJECTED", "DRAFT", "ARCHIVED"].includes(status)) {
    throw new Error("Invalid input");
  }

  await prisma.mod.update({
    where: { id: modId },
    data: { status: status as any },
  });

  revalidatePath("/admin/mods");
}
