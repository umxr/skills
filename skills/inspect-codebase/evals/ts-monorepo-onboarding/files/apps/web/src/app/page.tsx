import { ShipmentTable } from "@harbor/ui";
import { createClient } from "@harbor/api-client";

const api = createClient(process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:4000");

export default async function Home() {
  const shipments = await api.listShipments();
  return (
    <main>
      <h1>Shipments</h1>
      <ShipmentTable rows={shipments} />
    </main>
  );
}
