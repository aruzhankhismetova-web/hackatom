export const READINGS = [
  { day: "Wed", water: 19.6, greenhouse: 24.1, outside: 14.8, pulled: 7.5, headroom: 35.4, ph: 7.42, do: 7.3, ec: 732, nh3raw: 0.32, nh3filtered: 0.017, feed: 0.19, biomass: 18.0 },
  { day: "Thu", water: 21.5, greenhouse: 25.6, outside: 16.9, pulled: 8.1, headroom: 34.4, ph: 7.4, do: 7.9, ec: 765, nh3raw: 0.31, nh3filtered: 0.028, feed: 0.19, biomass: 18.1 },
  { day: "Fri", water: 20.1, greenhouse: 24.8, outside: 14.2, pulled: 9.3, headroom: 33.0, ph: 7.49, do: 7.7, ec: 762, nh3raw: 0.33, nh3filtered: 0.021, feed: 0.18, biomass: 18.2 },
  { day: "Sat", water: 20.6, greenhouse: 25.2, outside: 16.1, pulled: 11.1, headroom: 32.4, ph: 7.49, do: 7.1, ec: 787, nh3raw: 0.33, nh3filtered: 0.018, feed: 0.21, biomass: 18.2 },
  { day: "Sun", water: 22.1, greenhouse: 26.0, outside: 18.3, pulled: 14.5, headroom: 32.7, ph: 7.34, do: 7.8, ec: 791, nh3raw: 0.34, nh3filtered: 0.029, feed: 0.2, biomass: 18.3 },
  { day: "Mon", water: 22.2, greenhouse: 26.4, outside: 19.0, pulled: 15.7, headroom: 31.5, ph: 7.49, do: 7.5, ec: 782, nh3raw: 0.31, nh3filtered: 0.027, feed: 0.19, biomass: 18.4 },
  { day: "Tue", water: 21.2, greenhouse: 25.8, outside: 17.4, pulled: 17.8, headroom: 30.0, ph: 7.53, do: 7.9, ec: 824, nh3raw: 0.34, nh3filtered: 0.027, feed: 0.21, biomass: 18.4 },
];

export const DEFAULT_SUPPLIES = {
  waterLevelPct: 87,
  feedStockKg: 9.6,
  feedBagSizeKg: 25,
  phBufferMl: 340,
  phBufferFullMl: 500,
  nutrientL: 1.2,
  nutrientFullL: 2,
};

export const SUPPLY_STEPS = {
  water: 10,
  feed: 2.5,
  ph: 100,
  nutrient: 0.4,
};

export const CHART = {
  width: 335,
  padLeft: 36,
  padRight: 28,
  padTop: 8,
  padBottom: 20,
};

export const LIMITS = {
  doAction: 6,
  doWatch: 6.5,
  phMin: 6.8,
  phMax: 7.6,
  ammoniaAction: 0.1,
  ammoniaWatch: 0.05,
  headroomCeiling: 40,
  headroomTight: 0.4,
  ecAction: 900,
  ecWatch: 860,
  waterAction: 30,
  waterWatch: 50,
  feedActionDays: 3,
  feedWatchDays: 7,
  bottleLowPct: 35,
};

export function scaleX(index, count, width, padLeft, padRight = padLeft) {
  if (count <= 1) return (padLeft + width - padRight) / 2;
  return padLeft + (index / (count - 1)) * (width - padLeft - padRight);
}

export function scaleY(value, min, max, height, padTop, padBottom) {
  const span = max - min || 1;
  return padTop + (1 - (value - min) / span) * (height - padTop - padBottom);
}

export function polyline(values, width, height, min, max, padLeft, padTop, padBottom, padRight = padLeft) {
  return values
    .map((value, index) => {
      const x = scaleX(index, values.length, width, padLeft, padRight);
      const y = scaleY(value, min, max, height, padTop, padBottom);
      return `${index === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
}

export function risePercent(start, end) {
  if (!start) return 0;
  return ((end - start) / start) * 100;
}

export function removalPercent(raw, filtered) {
  if (!raw) return 0;
  return ((raw - filtered) / raw) * 100;
}

export function average(values) {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

export function daysOfStock(stock, perDay) {
  if (stock <= 0) return 0;
  if (perDay <= 0) return Infinity;
  return Math.floor(stock / perDay);
}

export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function roundTo(value, places) {
  const factor = 10 ** places;
  return Math.round((value + Number.EPSILON) * factor) / factor;
}

export function adjustSupply(supplies, key, delta) {
  const next = { ...supplies };
  if (key === "water") next.waterLevelPct = roundTo(clamp(supplies.waterLevelPct + delta, 0, 100), 0);
  if (key === "feed") next.feedStockKg = roundTo(clamp(supplies.feedStockKg + delta, 0, supplies.feedBagSizeKg), 1);
  if (key === "ph") next.phBufferMl = roundTo(clamp(supplies.phBufferMl + delta, 0, supplies.phBufferFullMl), 0);
  if (key === "nutrient") next.nutrientL = roundTo(clamp(supplies.nutrientL + delta, 0, supplies.nutrientFullL), 1);
  return next;
}

export function sanitizeSupplies(raw, defaults = DEFAULT_SUPPLIES) {
  const next = { ...defaults };
  if (!raw || typeof raw !== "object") return next;
  for (const key of ["waterLevelPct", "feedStockKg", "phBufferMl", "nutrientL"]) {
    const value = Number(raw[key]);
    if (Number.isFinite(value)) next[key] = value;
  }
  next.feedBagSizeKg = defaults.feedBagSizeKg;
  next.phBufferFullMl = defaults.phBufferFullMl;
  next.nutrientFullL = defaults.nutrientFullL;
  next.waterLevelPct = roundTo(clamp(next.waterLevelPct, 0, 100), 0);
  next.feedStockKg = roundTo(clamp(next.feedStockKg, 0, next.feedBagSizeKg), 1);
  next.phBufferMl = roundTo(clamp(next.phBufferMl, 0, next.phBufferFullMl), 0);
  next.nutrientL = roundTo(clamp(next.nutrientL, 0, next.nutrientFullL), 1);
  return next;
}

export function suppliesMatch(left, right) {
  return (
    left.waterLevelPct === right.waterLevelPct &&
    left.feedStockKg === right.feedStockKg &&
    left.phBufferMl === right.phBufferMl &&
    left.nutrientL === right.nutrientL
  );
}

export function assess(reading, supplies, feedPerDay) {
  const messages = [];
  let level = "steady";
  const rank = { steady: 0, watch: 1, action: 2 };
  const bump = (next, text) => {
    if (rank[next] > rank[level]) level = next;
    messages.push({ level: next, text });
  };

  if (reading.do < LIMITS.doAction) bump("action", "dissolved oxygen is low — check aeration");
  else if (reading.do < LIMITS.doWatch) bump("watch", "dissolved oxygen is softening");

  if (reading.ph < LIMITS.phMin || reading.ph > LIMITS.phMax) bump("watch", "pH is outside the 6.8–7.6 band");

  if (reading.nh3filtered >= LIMITS.ammoniaAction) bump("action", "ammonia after the biofilter is high");
  else if (reading.nh3filtered >= LIMITS.ammoniaWatch) bump("watch", "ammonia after the biofilter is climbing");

  if (reading.headroom / LIMITS.headroomCeiling < LIMITS.headroomTight) {
    bump("watch", "plant headroom is getting tight");
  }

  if (reading.ec >= LIMITS.ecAction) bump("action", "EC is at the salt-buildup ceiling");
  else if (reading.ec >= LIMITS.ecWatch) bump("watch", "EC is climbing toward 900 ppm");

  if (supplies.waterLevelPct < LIMITS.waterAction) bump("action", "sump water is low — check for leaks");
  else if (supplies.waterLevelPct < LIMITS.waterWatch) bump("watch", "sump water is under half");

  const feedDays = daysOfStock(supplies.feedStockKg, feedPerDay);
  if (feedDays < LIMITS.feedActionDays) bump("action", "fish feed runs out in under 3 days");
  else if (feedDays < LIMITS.feedWatchDays) bump("watch", "fish feed lasts under a week");

  const phPct = (supplies.phBufferMl / supplies.phBufferFullMl) * 100;
  if (phPct < LIMITS.bottleLowPct) bump("watch", "pH buffer is running low");

  const nutPct = (supplies.nutrientL / supplies.nutrientFullL) * 100;
  if (nutPct < LIMITS.bottleLowPct) bump("watch", "nutrient solution is running low");

  return { level, messages, feedDays, phPct, nutPct };
}

export function steadySummary(reading) {
  const removed = Math.round(removalPercent(reading.nh3raw, reading.nh3filtered));
  return `On ${reading.day}, the biofilter is clearing ${removed}% of ammonia · ${reading.headroom} mg/L of plant headroom`;
}
