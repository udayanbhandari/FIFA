import { expect, test } from "@playwright/test";

test.describe("StadiumIQ Playwright E2E Critical Journey", () => {
  test.beforeEach(async ({ page }) => {
    // Block actual API responses to keep E2E tests fully offline and deterministic
    await page.route("**/api/assist", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          answer: "The nearest restroom is restroom_north near Section 2.",
          confidence: 0.95,
          zone_reference: "restroom_north",
          suggested_actions: [{ action: "find_nearest", details: "Show route map" }],
          source: "gemini",
          language: "en",
        }),
      });
    });

    await page.route("**/api/assist/history/*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });

    await page.goto("/");
  });

  test("should allow fan to query assistant and receive answer", async ({ page }) => {
    // Select input field
    const input = page.locator('input[placeholder*="restrooms, medical"]');
    await expect(input).toBeVisible();

    // Type query
    await input.fill("where is the toilet?");
    await page.click('button[type="submit"]');

    // Verify response answer is rendered
    const chatBubble = page.locator(".chat-message.assistant").last();
    await expect(chatBubble).toContainText("restroom_north");
  });

  test("should support tab switching to sustainability dashboard", async ({ page }) => {
    // Locate navigation tab and click
    const sustTab = page.locator('button[role="tab"]:has-text("Sustainability")');
    await sustTab.click();

    // Verify forms display
    const attendanceInput = page.locator("#attendance-input");
    await expect(attendanceInput).toBeVisible();
    await expect(page.locator('button:has-text("Calculate Match Day")')).toBeVisible();
  });
});
