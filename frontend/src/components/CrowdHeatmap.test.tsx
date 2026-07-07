import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { describe, expect, test, vi } from "vitest";
import { useStadium } from "../hooks/useStadium";
import { CrowdHeatmap } from "./CrowdHeatmap";

const mockUseStadium = {
  state: {
    density: {
      zone_id: "concourse_north",
      zone_type: "concourse",
      current_density: 1.2,
      occupancy_count: 960,
      capacity: 2800,
      utilization_pct: 34.2,
      safety_status: "safe",
    },
    alerts: [],
  },
  checkZoneDensity: vi.fn(),
} as unknown as ReturnType<typeof useStadium>;

describe("CrowdHeatmap Component", () => {
  test("passes accessibility checks", async () => {
    const { container } = render(<CrowdHeatmap stadium={mockUseStadium} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test("renders selectors, zone buttons, and text equivalent data grids", () => {
    render(<CrowdHeatmap stadium={mockUseStadium} />);
    expect(screen.getByRole("img", { name: /stadium zone density/i })).toBeInTheDocument();
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByText("North Concourse")).toBeInTheDocument();
  });

  test("clicking update triggers density checks", async () => {
    render(<CrowdHeatmap stadium={mockUseStadium} />);
    const updateBtn = screen.getByRole("button", { name: /update crowd/i });
    await userEvent.click(updateBtn);
    expect(mockUseStadium.checkZoneDensity).toHaveBeenCalled();
  });
});
