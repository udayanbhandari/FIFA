import {
  AssistantResponse,
  CongestionAlert,
  CrowdQuery,
  FanQueryRecord,
  Language,
  MatchFootprint,
  SustainabilityComparison,
  SustainabilityQuery,
  WayfindingRoute,
  ZoneDensity,
} from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    ...(options?.headers || {}),
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `HTTP Error ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  // ── Crowd Intelligence ──
  getZoneDensity(query: CrowdQuery): Promise<ZoneDensity> {
    return request<ZoneDensity>("/crowd/density", {
      method: "POST",
      body: JSON.stringify(query),
    });
  },

  predictCongestion(zoneDensities: Record<string, number>, phase: string): Promise<CongestionAlert[]> {
    return request<CongestionAlert[]>("/crowd/predict", {
      method: "POST",
      body: JSON.stringify({
        zone_densities: zoneDensities,
        event_phase: phase,
        elapsed_minutes: 0,
      }),
    });
  },

  // ── Accessible Wayfinding ──
  getRoute(origin: string, destination: string, need: string): Promise<WayfindingRoute> {
    return request<WayfindingRoute>("/wayfinding/route", {
      method: "POST",
      body: JSON.stringify({
        origin_zone: origin,
        destination_zone: destination,
        accessibility_need: need,
      }),
    });
  },

  getNearestFacility(zone: string, type: string, need: string): Promise<{ facility_zone_id: string; route: WayfindingRoute }> {
    return request<{ facility_zone_id: string; route: WayfindingRoute }>("/wayfinding/nearest", {
      method: "POST",
      body: JSON.stringify({
        current_zone: zone,
        facility_type: type,
        accessibility_need: need,
      }),
    });
  },

  // ── Fan Assistant ──
  askAssistant(question: string, language: Language, zone: string, deviceId: string): Promise<AssistantResponse> {
    return request<AssistantResponse>("/assist", {
      method: "POST",
      body: JSON.stringify({
        question,
        language,
        current_zone: zone,
        device_id: deviceId,
      }),
    });
  },

  getHistory(deviceId: string): Promise<FanQueryRecord[]> {
    return request<FanQueryRecord[]>(`/assist/history/${deviceId}`);
  },

  // ── Sustainability ──
  getSustainabilityFootprint(query: SustainabilityQuery): Promise<MatchFootprint> {
    return request<MatchFootprint>("/sustainability/footprint", {
      method: "POST",
      body: JSON.stringify(query),
    });
  },

  compareSustainabilityFootprint(query: SustainabilityQuery): Promise<SustainabilityComparison> {
    return request<SustainabilityComparison>("/sustainability/compare", {
      method: "POST",
      body: JSON.stringify(query),
    });
  },

  getTargets(): Promise<{ fifa_target_kg_co2e_per_fan: number; metrics_tracked: string[] }> {
    return request<{ fifa_target_kg_co2e_per_fan: number; metrics_tracked: string[] }>("/sustainability/targets");
  },
};
