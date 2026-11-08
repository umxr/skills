import { describe, it, expect } from "vitest";
import { eta } from "./format";

describe("eta", () => {
  it("formats a date", () => {
    expect(eta("2024-01-02")).toBeTypeOf("string");
  });
});
