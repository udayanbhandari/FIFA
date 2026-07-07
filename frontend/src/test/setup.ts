import "@testing-library/jest-dom";
import * as axeMatchers from "vitest-axe/matchers";
import { expect } from "vitest";

// Register axe accessibility assertions matches in vitest
expect.extend(axeMatchers);
