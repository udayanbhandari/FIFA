import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { describe, expect, test, vi } from "vitest";
import { App } from "./App";

// Mock entire useStadium hook internally to decouple network
vi.mock("./hooks/useStadium", () => ({
  useStadium: () => ({
    state: {
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
      status: "System Ready",
    },
    deviceId: "test_dev_uuid",
    askAssistant: vi.fn(),
    loadHistory: vi.fn(),
    checkZoneDensity: vi.fn(),
    findRoute: vi.fn(),
    findNearest: vi.fn(),
    calculateSustainability: vi.fn(),
    clearError: vi.fn(),
  }),
}));

describe("App Integration Main Shell", () => {
  test("passes accessibility checks", async () => {
    const { container } = render(<App />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test("contains skip links, brand tags, and tab navigation landmarks", () => {
    render(<App />);
    expect(screen.getByRole("link", { name: /skip to main/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "StadiumIQ" })).toBeInTheDocument();
    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });

  test("tab navigation changes visible content panels", async () => {
    render(<App />);
    const tabSustainability = screen.getByRole("tab", { name: /🌱 sustainability/i });

    await userEvent.click(tabSustainability);
    expect(screen.getByRole("button", { name: /calculate match/i })).toBeInTheDocument();
  });
});
