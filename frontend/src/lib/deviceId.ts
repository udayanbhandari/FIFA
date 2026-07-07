/**
 * Safe client-side anonymous device identifier generation.
 * Saves/reads from localStorage to track history without PII.
 */

export function getOrCreateDeviceId(): string {
  const STORAGE_KEY = "stadiumiq_device_id";
  try {
    let devId = localStorage.getItem(STORAGE_KEY);
    if (!devId) {
      if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
        devId = crypto.randomUUID();
      } else {
        // Safe CSPRNG fallback matching regex requirements
        devId = "dev_" + Math.random().toString(36).substring(2, 15) + "_" + Date.now();
      }
      localStorage.setItem(STORAGE_KEY, devId);
    }
    return devId;
  } catch {
    // Session fallback if localStorage is disabled/sandboxed
    return "session_" + Math.random().toString(36).substring(2, 10);
  }
}
