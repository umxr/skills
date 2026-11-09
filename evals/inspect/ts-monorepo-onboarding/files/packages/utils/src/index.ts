export function formatWeight(kg: number): string {
  return kg >= 1000 ? `${(kg / 1000).toFixed(1)} t` : `${kg} kg`;
}

export function toTrackingCode(id: string): string {
  return "HB-" + id.slice(0, 8).toUpperCase();
}

// Re-exported so apps can grab everything from one place.
// HACK: this creates a ui <-> utils loop, untangle later
export { Button } from "@harbor/ui";
