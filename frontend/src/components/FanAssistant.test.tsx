import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { useStadium } from "../hooks/useStadium";
import { FanAssistant } from "./FanAssistant";

// Mock hooks return
const mockUseStadium = {
  state: {
    assistantResponse: null,
    history: [],
    loading: false,
    error: null,
    status: null,
  },
  deviceId: "test_dev_id",
  askAssistant: vi.fn(),
  loadHistory: vi.fn(),
} as unknown as ReturnType<typeof useStadium>;

describe("FanAssistant Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("passes accessibility checks", async () => {
    const { container } = render(<FanAssistant stadium={mockUseStadium} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test("renders input query box and chat welcome message", () => {
    render(<FanAssistant stadium={mockUseStadium} />);
    expect(screen.getByRole("log")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/restrooms, medical/)).toBeInTheDocument();
  });

  test("form submission fires state request callback", async () => {
    render(<FanAssistant stadium={mockUseStadium} />);
    const input = screen.getByPlaceholderText(/restrooms, medical/);
    const submit = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "Where is the train station?");
    await userEvent.click(submit);

    expect(mockUseStadium.askAssistant).toHaveBeenCalledWith(
      "Where is the train station?",
      "en",
      "concourse_north",
    );
  });
});
