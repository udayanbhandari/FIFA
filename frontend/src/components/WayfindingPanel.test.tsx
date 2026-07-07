import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { describe, expect, test, vi } from "vitest";
import { useStadium } from "../hooks/useStadium";
import { WayfindingPanel } from "./WayfindingPanel";

const mockUseStadium = {
  state: {
    route: {
      origin: "gate_north",
      destination: "seating_1",
      total_distance_meters: 150,
      estimated_minutes: 2.5,
      accessibility_score: 1.0,
      steps: [
        {
          from_zone: "gate_north",
          to_zone: "concourse_north",
          instruction: "Follow ramp north",
          distance_meters: 80,
          is_accessible: true,
          accessibility_features: ["ramp"],
        },
      ],
    },
    nearest: null,
  },
  findRoute: vi.fn(),
  findNearest: vi.fn(),
} as unknown as ReturnType<typeof useStadium>;

describe("WayfindingPanel Component", () => {
  test("passes accessibility checks", async () => {
    const { container } = render(<WayfindingPanel stadium={mockUseStadium} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test("renders profile selectors, dropdowns, and route list", () => {
    render(<WayfindingPanel stadium={mockUseStadium} />);
    expect(screen.getByRole("group", { name: /accessibility profile/i })).toBeInTheDocument();
    expect(screen.getByText("Follow ramp north")).toBeInTheDocument();
  });

  test("clicking submit triggers routing calculations", async () => {
    render(<WayfindingPanel stadium={mockUseStadium} />);
    const button = screen.getByRole("button", { name: /find accessible route/i });
    await userEvent.click(button);
    expect(mockUseStadium.findRoute).toHaveBeenCalled();
  });
});
