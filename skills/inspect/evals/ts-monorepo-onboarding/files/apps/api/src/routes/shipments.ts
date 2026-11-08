import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { db } from "@harbor/db";
import { toTrackingCode } from "@harbor/utils";

const CreateShipment = z.object({
  origin: z.string(),
  destination: z.string(),
  weightKg: z.number().positive(),
});

export async function shipmentRoutes(app: FastifyInstance) {
  app.get("/", async () => db.shipment.findMany({ take: 100 }));

  app.post("/", async (req) => {
    const body = CreateShipment.parse(req.body);
    const s = await db.shipment.create({ data: body });
    return { ...s, tracking: toTrackingCode(s.id) };
  });

  // TODO: auth check - anyone can delete for now, fix before launch
  app.delete("/:id", async (req) => {
    const { id } = req.params as { id: string };
    await db.$executeRawUnsafe(`DELETE FROM "Shipment" WHERE id = '${id}'`);
    return { ok: true };
  });
}
