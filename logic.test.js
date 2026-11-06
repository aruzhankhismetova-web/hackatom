import assert from "node:assert/strict";
import test from "node:test";
import {
  DEFAULT_SUPPLIES,
  READINGS,
  adjustSupply,
  assess,
  average,
  daysOfStock,
  polyline,
  removalPercent,
  risePercent,
  sanitizeSupplies,
  scaleX,
  scaleY,
  steadySummary,
  suppliesMatch,
} from "./logic.js";

test("week is the seven Ranchu days from the mock", () => {
  assert.deepEqual(
    READINGS.map((reading) => reading.day),
    ["Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue"],
  );
});

test("scale maps the plot edges", () => {
  assert.equal(scaleX(0, 7, 335, 36, 10), 36);
  assert.equal(scaleX(6, 7, 335, 36, 10), 325);
  assert.equal(scaleY(30, 10, 30, 150, 8, 20), 8);
  assert.equal(scaleY(10, 10, 30, 150, 8, 20), 130);
});

test("polyline starts at the first point and visits every reading", () => {
  const path = polyline([7.5, 8.1, 9.3], 335, 130, 0, 20, 36, 8, 20, 10);
  assert.equal(path[0], "M");
  assert.equal(path.split("L").length, 3);
});

test("nitrogen rise and biofilter removal match the logged week", () => {
  assert.equal(Math.round(risePercent(READINGS[0].pulled, READINGS[6].pulled)), 137);
  assert.equal(Math.round(removalPercent(READINGS[6].nh3raw, READINGS[6].nh3filtered)), 92);
});

test("feed stock lasts 49 days at the week's average", () => {
  const perDay = average(READINGS.map((reading) => reading.feed));
  assert.equal(perDay.toFixed(2), "0.20");
  assert.equal(daysOfStock(DEFAULT_SUPPLIES.feedStockKg, perDay), 49);
  assert.equal(daysOfStock(0, perDay), 0);
});

test("Tuesday's sample loop is steady", () => {
  const perDay = average(READINGS.map((reading) => reading.feed));
  const result = assess(READINGS[6], DEFAULT_SUPPLIES, perDay);
  assert.equal(result.level, "steady");
  assert.deepEqual(result.messages, []);
  assert.match(steadySummary(READINGS[6]), /On Tue, the biofilter is clearing 92%/);
});

test("low water outranks a watch", () => {
  const supplies = { ...DEFAULT_SUPPLIES, waterLevelPct: 12, phBufferMl: 40 };
  const result = assess(READINGS[6], supplies, 0.2);
  assert.equal(result.level, "action");
  assert.ok(result.messages.some((message) => message.text.includes("sump water")));
  assert.ok(result.messages.some((message) => message.level === "watch"));
});

test("supply steps clamp at empty and full", () => {
  const fed = adjustSupply(DEFAULT_SUPPLIES, "feed", -2.5);
  assert.equal(fed.feedStockKg, 7.1);
  assert.equal(adjustSupply(DEFAULT_SUPPLIES, "water", -200).waterLevelPct, 0);
  assert.equal(adjustSupply(DEFAULT_SUPPLIES, "nutrient", 5).nutrientL, 2);
  assert.equal(adjustSupply(DEFAULT_SUPPLIES, "ph", -100).phBufferMl, 240);
});

test("saved supplies cannot inflate container size", () => {
  const clean = sanitizeSupplies(
    {
      waterLevelPct: 140,
      feedStockKg: -3,
      feedBagSizeKg: 999,
      phBufferMl: 20,
      nutrientL: 5,
    },
    DEFAULT_SUPPLIES,
  );
  assert.equal(clean.waterLevelPct, 100);
  assert.equal(clean.feedStockKg, 0);
  assert.equal(clean.feedBagSizeKg, 25);
  assert.equal(clean.phBufferMl, 20);
  assert.equal(clean.nutrientL, 2);
  assert.equal(suppliesMatch(clean, DEFAULT_SUPPLIES), false);
  assert.equal(suppliesMatch(sanitizeSupplies(null), DEFAULT_SUPPLIES), true);
});
