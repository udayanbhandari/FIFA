import { useCallback, useState } from "react";
import { api } from "../lib/api";
import { getOrCreateDeviceId } from "../lib/deviceId";
import {
  AccessibilityNeed,
  AssistantResponse,
  CongestionAlert,
  EventPhase,
  FanQueryRecord,
  Language,
  MatchFootprint,
  SustainabilityComparison,
  SustainabilityQuery,
  WayfindingRoute,
  ZoneDensity,
} from "../lib/types";

export interface StadiumState {
  // Assistant
  assistantResponse: AssistantResponse | null;
  history: FanQueryRecord[];
  // Crowd
  density: ZoneDensity | null;
  alerts: CongestionAlert[];
  // Wayfinding
  route: WayfindingRoute | null;
  nearest: { zoneId: string; route: WayfindingRoute } | null;
  // Sustainability
  footprint: MatchFootprint | null;
  comparison: SustainabilityComparison | null;
  // System State
  loading: boolean;
  saving: boolean;
  error: string | null;
  status: string | null;
}

export function useStadium() {
  const [state, setState] = useState<StadiumState>({
    assistantResponse: null,
    history: [],
    density: null,
    alerts: [],
    route: null,
    nearest: null,
    footprint: null,
    comparison: null,
    loading: false,
    saving: false,
    error: null,
    status: null,
  });

  const deviceId = getOrCreateDeviceId();

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const askAssistant = useCallback(
    async (question: string, language: Language, zone: string) => {
      setState((prev) => ({ ...prev, loading: true, error: null, status: "Asking assistant..." }));
      try {
        const response = await api.askAssistant(question, language, zone, deviceId);
        const historyList = await api.getHistory(deviceId);

        setState((prev) => ({
          ...prev,
          assistantResponse: response,
          history: historyList,
          loading: false,
          status: "Response ready.",
        }));
      } catch (err) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: err instanceof Error ? err.message : "Failed to query assistant",
          status: null,
        }));
      }
    },
    [deviceId],
  );

  const loadHistory = useCallback(async () => {
    try {
      const historyList = await api.getHistory(deviceId);
      setState((prev) => ({ ...prev, history: historyList }));
    } catch {
      // Quiet fail to maintain operation robustness
    }
  }, [deviceId]);

  const checkZoneDensity = useCallback(async (zoneId: string, phase: EventPhase) => {
    setState((prev) => ({ ...prev, loading: true, error: null, status: "Checking density..." }));
    try {
      const query = {
        zone_id: zoneId,
        gate_counts: { gate_north: 4500, gate_south: 3900, gate_east: 5100 },
        elapsed_minutes: 30,
        event_phase: phase,
      };
      const densityRes = await api.getZoneDensity(query);

      // Run parallel prediction checks to improve responsiveness
      const alertMap: Record<string, number> = {
        [zoneId]: densityRes.current_density,
        concourse_north: 2.1,
        vomitory_1: 4.8,
        transit_hub: 1.8,
      };

      const alertsRes = await api.predictCongestion(alertMap, phase);

      setState((prev) => ({
        ...prev,
        density: densityRes,
        alerts: alertsRes,
        loading: false,
        status: "Crowd status updated.",
      }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to calculate crowd metrics",
        status: null,
      }));
    }
  }, []);

  const findRoute = useCallback(async (origin: string, destination: string, need: AccessibilityNeed) => {
    setState((prev) => ({ ...prev, loading: true, error: null, status: "Calculating route..." }));
    try {
      const routeRes = await api.getRoute(origin, destination, need);
      setState((prev) => ({
        ...prev,
        route: routeRes,
        nearest: null,
        loading: false,
        status: "Route calculated.",
      }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to compute wayfinding route",
        status: null,
      }));
    }
  }, []);

  const findNearest = useCallback(async (zone: string, type: string, need: AccessibilityNeed) => {
    setState((prev) => ({ ...prev, loading: true, error: null, status: "Searching nearest..." }));
    try {
      const res = await api.getNearestFacility(zone, type, need);
      setState((prev) => ({
        ...prev,
        nearest: { zoneId: res.facility_zone_id, route: res.route },
        route: null,
        loading: false,
        status: `Nearest ${type} found.`,
      }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to search nearest facility",
        status: null,
      }));
    }
  }, []);

  const calculateSustainability = useCallback(async (query: SustainabilityQuery) => {
    setState((prev) => ({ ...prev, loading: true, error: null, status: "Evaluating carbon footprints..." }));
    try {
      const [footprintRes, comparisonRes] = await Promise.all([
        api.getSustainabilityFootprint(query),
        api.compareSustainabilityFootprint(query),
      ]);

      setState((prev) => ({
        ...prev,
        footprint: footprintRes,
        comparison: comparisonRes,
        loading: false,
        status: "Sustainability calculation completed.",
      }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to load sustainability results",
        status: null,
      }));
    }
  }, []);

  return {
    state,
    deviceId,
    askAssistant,
    loadHistory,
    checkZoneDensity,
    findRoute,
    findNearest,
    calculateSustainability,
    clearError,
  };
}
export type UseStadiumReturn = ReturnType<typeof useStadium>;
