/**
 * Shared Type Declarations for StadiumIQ.
 * Matches backend Pydantic models field-for-field.
 */

export type ZoneType =
  | "gate"
  | "concourse"
  | "seating"
  | "concession"
  | "medical"
  | "restroom"
  | "vomitory"
  | "parking"
  | "transit_hub";

export type AccessibilityNeed = "none" | "wheelchair" | "visual" | "hearing" | "cognitive";

export type TransportMode = "metro" | "bus" | "rideshare" | "walk" | "accessible_shuttle" | "bicycle";

export type EventPhase =
  | "pre_match"
  | "kickoff"
  | "halftime"
  | "second_half"
  | "full_time"
  | "post_match";

export type Language = "en" | "es" | "fr" | "ar" | "pt" | "de" | "ja" | "ko" | "zh";

export interface CrowdQuery {
  zone_id: string;
  gate_counts: Record<string, number>;
  elapsed_minutes: number;
  event_phase: EventPhase;
  stadium_capacity?: number;
}

export interface ZoneDensity {
  zone_id: string;
  zone_type: ZoneType;
  current_density: number;
  occupancy_count: number;
  capacity: number;
  utilization_pct: number;
  safety_status: "safe" | "caution" | "critical";
}

export interface CongestionAlert {
  zone_id: string;
  predicted_density: number;
  risk_level: "low" | "medium" | "high" | "critical";
  recommended_action: string;
  time_horizon_minutes: number;
}

export interface RouteStep {
  from_zone: string;
  to_zone: string;
  instruction: string;
  distance_meters: number;
  is_accessible: boolean;
  accessibility_features: string[];
}

export interface WayfindingRoute {
  origin: string;
  destination: string;
  steps: RouteStep[];
  total_distance_meters: number;
  estimated_minutes: number;
  accessibility_score: number;
}

export interface SuggestedAction {
  action: string;
  details: string;
}

export interface AssistantResponse {
  answer: string;
  suggested_actions: SuggestedAction[];
  zone_reference: string | null;
  confidence: number;
  source: "gemini" | "rules" | "cache";
  language: Language;
}

export interface SustainabilityQuery {
  attendance: number;
  transport_mix: Record<string, number>;
  energy_kwh: number;
  waste_kg: number;
  water_liters: number;
}

export interface MatchFootprint {
  total_kg_co2e: number;
  transport_kg_co2e: number;
  energy_kg_co2e: number;
  waste_kg_co2e: number;
  water_kg_co2e: number;
  per_fan_kg_co2e: number;
  transport_breakdown: Record<string, number>;
}

export interface SustainabilityComparison {
  match_footprint: MatchFootprint;
  fifa_target_kg_co2e: number;
  difference_kg_co2e: number;
  on_target: boolean;
  recommendations: string[];
}

export interface FanQueryRecord {
  id?: string;
  device_id: string;
  question: string;
  answer: string;
  source: string;
  language: Language;
  created_at?: string;
}
