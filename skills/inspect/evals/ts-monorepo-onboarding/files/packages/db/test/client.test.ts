import { describe, it, expect } from "vitest";
import { db } from "../src";

describe("db", () => {
  it("exports a client", () => {
    expect(db).toBeDefined();
  });
});
