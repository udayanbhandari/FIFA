# ACCESSIBILITY Blueprint

Rules extracted from semantic HTML, ARIA patterns, color handling, focus management, and automated testing.
Every rule is domain-agnostic and applies to any project on any topic.

---

RULE: Semantic Elements Before ARIA
WHAT: Every element uses the most semantic HTML element available: `<section>` with `aria-labelledby` for content regions, `<form>` with `aria-labelledby` for forms, `<fieldset>` and `<legend>` for input groups, `<table>` with `<caption>`, `<th scope>`, and `<thead>/<tbody>` for tabular data, `<header>` for the page header, `<main>` for the primary content. A `<div>` is used only when no semantic element applies (e.g., the bar chart visual container).
WHY IT SCORES: Semantic HTML is the foundation of accessibility. Evaluators detect `<div>` soup as an accessibility anti-pattern. Correct semantic elements provide screen reader navigation landmarks for free.
HOW TO APPLY: Before using a `<div>`, ask: "Is there a semantic element for this?" Use `<section>` for distinct content areas, `<nav>` for navigation, `<article>` for self-contained content, `<form>` for forms, `<table>` for data, `<fieldset>/<legend>` for input groups. Add `aria-labelledby` pointing to the section's heading.
SIGNAL IN REPO: frontend/src/components/ResultBreakdown.tsx (section with aria-labelledby, table with caption, thead, th scope), frontend/src/components/CalculatorForm.tsx (form with aria-labelledby, fieldset/legend for each group), frontend/src/App.tsx (header, main elements)

---

RULE: Single h1, Strict Heading Hierarchy
WHAT: The page has exactly one `<h1>` (in the app header). Sections use `<h2>`, subsections use `<h3>`. Headings never skip levels. Every section's heading is referenced by the section's `aria-labelledby` attribute.
WHY IT SCORES: Heading hierarchy is one of the most checked accessibility rules. Screen reader users navigate by headings, so skipped levels create confusion. Evaluators flag multiple h1 elements and skipped levels as violations.
HOW TO APPLY: Use exactly one `<h1>` per page. Each major section gets an `<h2>`. Subsections get `<h3>`. Never skip from h2 to h4. Give every heading an `id` so sections can reference it with `aria-labelledby`.
SIGNAL IN REPO: frontend/src/App.tsx (one h1: "Carbon Footprint Awareness Platform"), frontend/src/components/CalculatorForm.tsx (h2: "Estimate your annual footprint"), frontend/src/components/ResultBreakdown.tsx (h2: "Your estimated footprint", h3: "Breakdown by category")

---

RULE: Every Interactive Element Has an Accessible Name
WHAT: Every `<input>` has an associated `<label htmlFor>`. Every `<select>` has a `<label>`. Every `<button>` has visible text content. Every `<section>` has `aria-labelledby` pointing to its heading. Every `<form>` has `aria-labelledby`. Every bar chart row has an `aria-label` with the full value.
WHY IT SCORES: Missing accessible names are the most common WCAG violation. Evaluators flag inputs without labels, buttons without text, and regions without names as critical failures.
HOW TO APPLY: For every `<input>`, create a `<label htmlFor={id}>`. For every `<button>`, include visible text. For every `<section>`, add `aria-labelledby={headingId}`. For custom visual elements (bar chart rows), add `aria-label` with the full description including the value.
SIGNAL IN REPO: frontend/src/components/NumberField.tsx (label htmlFor={id} on every input), frontend/src/components/ResultBreakdown.tsx (aria-label on bar-row divs with category and value), frontend/src/components/CalculatorForm.tsx (label for every select)

---

RULE: Form Inputs Have aria-describedby for Hints
WHAT: When an input has helper text, it is associated via `aria-describedby` pointing to a hint element. The hint element has an `id` derived from the input's `id` (e.g., `${id}-hint`). When no hint exists, `aria-describedby` is omitted entirely (not set to undefined or empty string).
WHY IT SCORES: Evaluators check that hint text is programmatically associated with inputs, not just visually adjacent. The conditional rendering (omit when no hint) avoids empty aria-describedby, which is an anti-pattern.
HOW TO APPLY: Create a reusable input component that accepts an optional `hint` prop. If hint is provided, render a `<span id="${id}-hint">` and set `aria-describedby="${id}-hint"` on the input. If no hint, omit aria-describedby entirely.
SIGNAL IN REPO: frontend/src/components/NumberField.tsx (lines 30–53: conditional hintId, aria-describedby only when hint exists), frontend/src/components/NumberField.test.tsx (test that aria-describedby is present with hint and absent without)

---

RULE: Loading States Use aria-busy
WHAT: Buttons that trigger async operations show `aria-busy={loading}` when the operation is in progress. The button text changes to indicate the loading state ("Calculating…", "Saving…"). The button is also `disabled` during loading to prevent double-submission.
WHY IT SCORES: Screen readers announce `aria-busy` state changes to users. Evaluators check that loading states are communicated accessibly, not just visually. The combination of aria-busy, disabled, and changed text is comprehensive.
HOW TO APPLY: For every button that triggers an async operation, add `aria-busy={loading}` and `disabled={loading}`. Change the button text to show the loading state. Use a gerund ("Calculating…") to indicate ongoing action.
SIGNAL IN REPO: frontend/src/components/CalculatorForm.tsx (line 164: `aria-busy={loading}` on submit button), frontend/src/App.tsx (line 40: `aria-busy={saving}` on save button), frontend/src/components/CalculatorForm.test.tsx (line 79: test asserts aria-busy="true")

---

RULE: Async Results Announced via Live Regions
WHAT: Dynamic content updates are announced to screen readers using ARIA live regions. Error messages use `role="alert" aria-live="assertive"` (high priority). Status messages use `role="status"` with polite priority (visually hidden). The status text changes when results are ready ("Your footprint results and personalized insights are ready below") or when an entry is saved ("Entry saved to your history").
WHY IT SCORES: Live regions are the primary mechanism for announcing dynamic content to screen readers. Evaluators check for their presence when content updates asynchronously. Having both assertive (errors) and polite (status) regions demonstrates understanding of the ARIA live region model.
HOW TO APPLY: Create a `role="alert" aria-live="assertive"` container for error messages. Create a `role="status"` container (visually hidden) for status updates. Update the text content when async operations complete. Keep both containers in the DOM always (just empty when no message).
SIGNAL IN REPO: frontend/src/App.tsx (lines 28–33: role="alert" for errors, role="status" visually-hidden for status), frontend/src/hooks/useFootprint.ts (lines 47, 63: status messages set after async completion)

---

RULE: Data Visualizations Have Text Equivalents
WHAT: The bar chart is a visual-only element (`role="img"` with `aria-label` describing it). Immediately below it is a data table with the same information in an accessible format: `<table>` with `<caption>` (visually hidden), `<th scope="col">` for headers, `<th scope="row">` for row headers. Users who cannot see the chart get the same information from the table.
WHY IT SCORES: WCAG requires that information conveyed visually be available in text form. A canvas chart without a text equivalent is an accessibility failure. The combination of role="img" + data table is the gold standard pattern.
HOW TO APPLY: Wrap visual-only charts in a container with `role="img"` and `aria-label="Description of what the chart shows"`. Immediately follow with a `<table>` that contains the same data. Add a visually-hidden `<caption>`. Use `scope="col"` and `scope="row"` on headers.
SIGNAL IN REPO: frontend/src/components/ResultBreakdown.tsx (lines 40–57: role="img" chart, lines 60–76: accessible data table with caption, th scope="col", th scope="row")

---

RULE: Color Never Conveys Information Alone
WHAT: When color indicates status (over/under target), a text indicator is always paired with it: "↑" for above target, "↓" for below target. A visually hidden span provides the full text explanation. The CSS class names (`over`, `under`) are semantic, not presentational.
WHY IT SCORES: WCAG 1.4.1 requires that color is not the sole means of conveying information. Evaluators check for this by looking at colored elements and verifying text alternatives. Directional arrows (↑/↓) are a clean solution.
HOW TO APPLY: For every element that uses color to indicate status, add a text indicator (arrow, icon, or word). Add a visually-hidden span with the full explanation. Use semantic class names that describe the state, not the appearance.
SIGNAL IN REPO: frontend/src/components/ResultBreakdown.tsx (lines 23–31: "↑" and "↓" indicators + visually-hidden explanation), frontend/src/components/HistoryPanel.tsx (lines 29–38: "▼ Down" and "▲ Up" text with color)

---

RULE: AA Contrast with Documented Ratios
WHAT: All colors are chosen to meet WCAG AA contrast ratios (≥4.5:1 for normal text, ≥3:1 for large text and UI components). Contrast ratios are documented inline in CSS comments. Dark mode has its own complete color palette with independently verified contrast ratios.
WHY IT SCORES: Documented contrast ratios prove the developer tested colors, not just eyeballed them. Evaluators that compute contrast from CSS variables can verify compliance. Having both light and dark modes with verified contrast is exceptional.
HOW TO APPLY: Choose colors and document their contrast ratio against their background in CSS comments. Use WebAIM's contrast checker to verify. Create separate CSS variables for dark mode with independently verified ratios. Test with browser dev tools in both modes.
SIGNAL IN REPO: frontend/src/styles/theme.css (lines 1–5: comment stating WCAG AA compliance; line 10: `--text: #14201b; /* ~15:1 on surface */`; line 11: `--muted: #44524c; /* ~7:1 on surface */`; lines 285–301: dark mode with contrast ratios documented)

---

RULE: Focus-Visible for Keyboard Users
WHAT: A global `:focus-visible` rule provides a visible focus indicator (3px solid outline with offset) for all focusable elements. Additional focus styles are applied to specific elements (table rows, bar chart rows) for enhanced keyboard navigation. The focus color has sufficient contrast.
WHY IT SCORES: Focus visibility is required for keyboard accessibility. Evaluators check for `:focus-visible` rules and verify the focus indicator is visible. Enhanced focus on interactive data elements shows attention to keyboard usability beyond the minimum.
HOW TO APPLY: Add a global `:focus-visible` rule with a contrasting outline. Add specific focus styles for custom interactive elements (data rows, chart elements). Use `outline-offset` to avoid overlap with content.
SIGNAL IN REPO: frontend/src/styles/theme.css (lines 44–48: global :focus-visible, lines 182–186: .bar-row:focus-visible, lines 244–248: table tr:focus-visible)

---

RULE: Reduced Motion is Respected
WHAT: A `@media (prefers-reduced-motion: reduce)` query disables ALL transitions and animations with `!important`. This is a blanket rule that covers all elements, ensuring no motion occurs for users who have requested reduced motion.
WHY IT SCORES: Respecting reduced-motion preferences is a WCAG requirement. The blanket approach (all elements, !important) is more reliable than disabling individual animations. Evaluators check for the presence of this media query.
HOW TO APPLY: Add `@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }` to your global stylesheet. Place it after all other transition/animation rules so it overrides them.
SIGNAL IN REPO: frontend/src/styles/theme.css (lines 278–283: blanket reduced-motion override with `* { transition: none !important; animation: none !important; }`)

---

RULE: jsx-a11y Lint Rules in CI
WHAT: ESLint is configured with `eslint-plugin-jsx-a11y` in recommended mode, running as part of `npm run lint` and enforced in CI. This catches accessibility violations at lint time, before the code is even tested.
WHY IT SCORES: Lint-time accessibility checking is a proactive quality signal. It catches common violations (missing alt text, unlabeled inputs, bad ARIA usage) before they reach the test suite. Evaluators value this as a "shift left" accessibility practice.
HOW TO APPLY: Install `eslint-plugin-jsx-a11y`. Add it to your ESLint config in recommended mode. Run lint in CI. Let it fail the build on violations.
SIGNAL IN REPO: frontend/eslint.config.js (lines 23–26: jsxA11y.flatConfigs.recommended applied to src/**/*.{ts,tsx}), .github/workflows/ci.yml (line 53: "Lint (ESLint + jsx-a11y accessibility rules)")

---

RULE: Skip Link for Keyboard Navigation
WHAT: The first element in the page is a skip link (`<a class="skip-link" href="#main">Skip to main content</a>`) that is visually hidden until focused. It allows keyboard users to bypass the header and go directly to the main content.
WHY IT SCORES: Skip links are a WCAG 2.4.1 requirement. Evaluators check for their presence as a basic accessibility feature. The CSS pattern (hidden until focused) is the standard implementation.
HOW TO APPLY: Add a skip link as the very first element in the body. Link it to `#main` and give the main content area `id="main"`. Style it off-screen by default and visible on `:focus`.
SIGNAL IN REPO: frontend/src/App.tsx (lines 17–19: skip link as first element), frontend/src/styles/theme.css (lines 50–62: .skip-link positioned off-screen, visible on :focus)
