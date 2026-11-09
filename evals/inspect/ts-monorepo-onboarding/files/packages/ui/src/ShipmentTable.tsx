import { formatWeight } from "@harbor/utils";

export function ShipmentTable({ rows }: { rows: { id: string; origin: string; destination: string; weightKg: number }[] }) {
  return (
    <table>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id}>
            <td>{r.origin}</td>
            <td>{r.destination}</td>
            <td>{formatWeight(r.weightKg)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
