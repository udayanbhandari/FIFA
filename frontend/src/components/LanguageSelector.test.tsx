import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { describe, expect, test, vi } from "vitest";
import { LanguageSelector } from "./LanguageSelector";

describe("LanguageSelector Component", () => {
  test("passes accessibility checks", async () => {
    const { container } = render(<LanguageSelector value="en" onChange={vi.fn()} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test("renders select box with list options", () => {
    render(<LanguageSelector value="en" onChange={vi.fn()} />);
    const select = screen.getByRole("combobox");
    expect(select).toBeInTheDocument();
    expect(screen.getByText("English (EN)")).toBeInTheDocument();
    expect(screen.getByText("Español (ES)")).toBeInTheDocument();
  });

  test("onChange callback triggers on user choice", async () => {
    const handleChange = vi.fn();
    render(<LanguageSelector value="en" onChange={handleChange} />);
    const select = screen.getByRole("combobox");

    await userEvent.selectOptions(select, "es");
    expect(handleChange).toHaveBeenCalledWith("es");
  });
});
