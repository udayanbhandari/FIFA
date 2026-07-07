/* eslint-disable @typescript-eslint/no-explicit-any */
import "vitest-axe";

declare module "vitest" {
  export interface Assertion<T = any> extends vitestAxe.AxeMatchers<T> {}
  export interface AsymmetricMatchersContaining extends vitestAxe.AxeMatchers {}
}
