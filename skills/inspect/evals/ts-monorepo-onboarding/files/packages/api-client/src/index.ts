export type Shipment = { id: string; origin: string; destination: string; weightKg: number; status: string };

export function createClient(baseUrl: string) {
  return {
    async listShipments(): Promise<Shipment[]> {
      const res = await fetch(`${baseUrl}/shipments`);
      return res.json();
    },
  };
}
