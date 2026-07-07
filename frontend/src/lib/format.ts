/**
 * Pure formatting and localization helpers.
 * Zero imports from React or API client. Fully referentially transparent.
 */

/**
 * Format zone names from raw keys to friendly labels
 * e.g. "concourse_north" -> "North Concourse"
 */
export function formatZoneName(zoneId: string): string {
  if (!zoneId) return "";
  return zoneId
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .reverse()
    .join(" ");
}

/**
 * Render density float values into readable text with units
 */
export function formatDensity(density: number): string {
  return `${density.toFixed(1)} P/m²`;
}

/**
 * Format CO2 emissions into kilograms or metric tonnes depending on value size
 */
export function formatCO2(kg: number): string {
  if (kg >= 1000) {
    return `${(kg / 1000).toFixed(1)} t CO₂e`;
  }
  return `${kg.toLocaleString()} kg CO₂e`;
}

/**
 * Format route durations in minutes into hours/minutes
 */
export function formatDuration(minutes: number): string {
  if (minutes < 1) {
    return "Less than a minute";
  }
  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  }
  return `${Math.round(minutes)} min`;
}

/**
 * Localize ISO date strings to friendly display representation
 */
export function formatDate(isoString: string): string {
  try {
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}
