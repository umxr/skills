import Fastify from "fastify";
import { shipmentRoutes } from "./routes/shipments";
import { webhookRoutes } from "./routes/webhooks";

const app = Fastify({ logger: true });

app.register(shipmentRoutes, { prefix: "/shipments" });
app.register(webhookRoutes, { prefix: "/webhooks" });

app.listen({ port: Number(process.env.PORT ?? 4000), host: "0.0.0.0" });
