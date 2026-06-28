import "dotenv/config";
import { PrismaClient } from "../src/generated/prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import bcrypt from "bcryptjs";

const adapter = new PrismaPg(process.env.DATABASE_URL!);
const prisma = new PrismaClient({ adapter });

async function main() {
  const email = process.env.AUTH_ADMIN_EMAIL || "admin@modhub.dev";
  const password = process.env.AUTH_ADMIN_PASSWORD;

  if (!password) {
    console.error("❌ AUTH_ADMIN_PASSWORD is not set in .env");
    console.log("Add this to your .env file:");
    console.log('AUTH_ADMIN_PASSWORD="your-admin-password"');
    process.exit(1);
  }

  const passwordHash = await bcrypt.hash(password, 12);
  console.log(`Password hash generated for ${email}`);

  const user = await prisma.user.upsert({
    where: { email },
    update: {
      passwordHash,
      role: "ADMIN",
      name: "Admin",
    },
    create: {
      email,
      name: "Admin",
      role: "ADMIN",
      passwordHash,
    },
  });

  console.log(`✅ Admin user "${user.name}" created/updated:`);
  console.log(`   Email:    ${email}`);
  console.log(`   Password: ${password}`);
  console.log(`   Role:     ${user.role}`);
  console.log(`   ID:       ${user.id}`);
}

main()
  .catch((e) => {
    console.error("Error:", e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
