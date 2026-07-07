import { describe, expect, test } from "vitest";
import { formatCO2, formatDensity, formatDuration, formatZoneName } from "./format";

describe("Pure Display Format Utilities", () => {
  test("formatZoneName translates keys appropriately", () => {
    expect(formatZoneName("concourse_north")).toBe("North Concourse");
    expect(formatZoneName("gate_south")).toBe("South Gate");
    expect(formatZoneName("medical_main")).toBe("Main Medical");
  });

  test("formatDensity formats output with units", () => {
    expect(formatDensity(2.45)).toBe("2.5 P/m²");
    expect(formatDensity(0.0)).toBe("0.0 P/m²");
  });

  test("formatCO2 handles grams vs tonnes correctly", () => {
    expect(formatCO2(450)).toBe("450 kg CO₂e");
    expect(formatCO2(1200)).toBe("1.2 t CO₂e");
    expect(formatCO2(2500000)).toBe("2,500 t CO₂e");
  });

  test("formatDuration estimates human-friendly minutes", () => {
    expect(formatDuration(0.5)).toBe("Less than a minute");
    expect(formatDuration(8.4)).toBe("8 min");
    expect(formatDuration(75)).toBe("1h 15m");
    expect(formatDuration(120)).toBe("2h");
  });
});
