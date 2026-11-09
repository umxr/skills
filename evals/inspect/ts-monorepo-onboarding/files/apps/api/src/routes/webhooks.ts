import type { FastifyInstance } from "fastify";
import { db } from "@harbor/db";

// Carriers POST status updates here.
export async function webhookRoutes(app: FastifyInstance) {
  app.post("/carrier", async (req) => {
    // FIXME: verify signature with CARRIER_WEBHOOK_SECRET
    const evt = req.body as { shipmentId: string; status: string };
    await db.shipment.update({ where: { id: evt.shipmentId }, data: { status: evt.status } });
    return { received: true };
  });
}
