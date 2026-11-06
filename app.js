import {
  CHART,
  DEFAULT_SUPPLIES,
  READINGS,
  SUPPLY_STEPS,
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

const COLORS = {
  water: "#4FB3A9",
  greenhouse: "#9ED968",
  outside: "#E8A33D",
  nitrogen: "#7FD4A8",
  ph: "#C98FE0",
  biomass: "#7CA9E0",
};

const NS = "http://www.w3.org/2000/svg";
const STOCK_KEY = "greenhouse.ranchu.supplies";
const DAY_KEY = "greenhouse.ranchu.day";

const feedPerDay = average(READINGS.map((reading) => reading.feed));

let activeDay = loadDay();
let supplies = loadSupplies();

const $ = (id) => document.getElementById(id);

function loadDay() {
  try {
    const raw = sessionStorage.getItem(DAY_KEY);
    if (raw == null) return READINGS.length - 1;
    const day = Number(raw);
    if (Number.isInteger(day) && day >= 0 && day < READINGS.length) return day;
  } catch {
    /* session storage can be blocked */
  }
  return READINGS.length - 1;
}

function loadSupplies() {
  try {
    return sanitizeSupplies(JSON.parse(localStorage.getItem(STOCK_KEY)));
  } catch {
    return sanitizeSupplies(null);
  }
}

function saveSupplies() {
  try {
    localStorage.setItem(STOCK_KEY, JSON.stringify(supplies));
  } catch {
    /* ignore quota and private mode */
  }
}

function saveDay() {
  try {
    sessionStorage.setItem(DAY_KEY, String(activeDay));
  } catch {
    /* ignore */
  }
}

function svgEl(name, attrs) {
  const node = document.createElementNS(NS, name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}

function setRich(id, parts) {
  const node = $(id);
  node.replaceChildren();
  for (const part of parts) {
    if (typeof part === "string") {
      node.append(part);
    } else {
      const mark = document.createElement("span");
      mark.className = "hl";
      mark.textContent = part.hl;
      node.append(mark);
    }
  }
}

function showTip(tip, event, text) {
  tip.hidden = false;
  tip.textContent = text;
  const wrap = tip.parentElement.getBoundingClientRect();
  const width = tip.offsetWidth;
  const height = tip.offsetHeight;
  let left = event.clientX - wrap.left + 12;
  let top = event.clientY - wrap.top - height - 10;
  if (top < 6) top = event.clientY - wrap.top + 14;
  left = Math.max(6, Math.min(left, wrap.width - width - 6));
  top = Math.max(6, Math.min(top, wrap.height - height - 6));
  tip.style.left = `${left}px`;
  tip.style.top = `${top}px`;
}

function hideTips() {
  for (const tip of document.querySelectorAll(".tooltip")) tip.hidden = true;
}

function bindHover(node, tip, textOf) {
  const show = (event) => showTip(tip, event, textOf());
  node.addEventListener("pointerenter", (event) => {
    if (event.pointerType !== "touch") show(event);
  });
  node.addEventListener("pointermove", (event) => {
    if (event.pointerType !== "touch") show(event);
  });
  node.addEventListener("pointerleave", (event) => {
    if (event.pointerType !== "touch") tip.hidden = true;
  });
}

function selectDay(index, tip, event, message) {
  const changed = activeDay !== index;
  activeDay = index;
  saveDay();
  if (changed) renderAll();
  if (tip && event) showTip(tip, event, message);
}

function prepare(svg) {
  svg.replaceChildren();
}

function addFrame(svg, height, min, max, ticks, formatTick = (value) => String(value)) {
  const { width, padLeft, padRight, padTop, padBottom } = CHART;
  for (const tick of ticks) {
    const y = scaleY(tick, min, max, height, padTop, padBottom);
    svg.append(
      svgEl("line", {
        x1: String(padLeft),
        y1: String(y),
        x2: String(width - padRight),
        y2: String(y),
        stroke: "#25352B",
        "stroke-width": "1",
      }),
    );
    const label = svgEl("text", { x: "0", y: String(y + 3), class: "axis-label" });
    label.textContent = formatTick(tick);
    svg.append(label);
  }
  const slot = (width - padLeft - padRight) / READINGS.length;
  READINGS.forEach((reading, index) => {
    const x = scaleX(index, READINGS.length, width, padLeft, padRight);
    if (index === activeDay) {
      svg.append(
        svgEl("rect", {
          x: String(x - slot / 2),
          y: String(padTop),
          width: String(slot),
          height: String(height - padTop - padBottom),
          fill: COLORS.water,
          "fill-opacity": "0.14",
        }),
      );
    }
    const day = svgEl("text", {
      x: String(x),
      y: String(height - 3),
      class: index === activeDay ? "axis-label is-active" : "axis-label",
      "text-anchor": "middle",
    });
    day.textContent = reading.day;
    svg.append(day);
  });
}

function addGradient(svg, id, color) {
  const defs = svgEl("defs", {});
  const gradient = svgEl("linearGradient", { id, x1: "0", y1: "0", x2: "0", y2: "1" });
  gradient.append(
    svgEl("stop", { offset: "0%", "stop-color": color, "stop-opacity": "0.5" }),
    svgEl("stop", { offset: "100%", "stop-color": color, "stop-opacity": "0.02" }),
  );
  defs.append(gradient);
  svg.append(defs);
}

function addStroke(svg, d, color, extra = {}) {
  svg.append(
    svgEl("path", {
      d,
      fill: "none",
      stroke: color,
      "stroke-width": "2.3",
      ...extra,
    }),
  );
}

function addDays(svg, tip, height, summary) {
  const { width, padLeft, padRight, padTop, padBottom } = CHART;
  const slot = (width - padLeft - padRight) / READINGS.length;
  READINGS.forEach((reading, index) => {
    const x = scaleX(index, READINGS.length, width, padLeft, padRight);
    const hit = svgEl("rect", {
      class: "pt",
      x: String(x - slot / 2),
      y: String(padTop),
      width: String(slot),
      height: String(height - padTop - padBottom),
      fill: "transparent",
    });
    const text = () => summary(reading);
    bindHover(hit, tip, text);
    hit.addEventListener("click", (event) => selectDay(index, tip, event, text()));
    svg.append(hit);
  });
}

function addPoint(svg, tip, x, y, color, index, textOf) {
  const hit = svgEl("circle", {
    class: "pt",
    cx: String(x),
    cy: String(y),
    r: "11",
    fill: "transparent",
  });
  const title = svgEl("title", {});
  title.textContent = textOf();
  hit.append(title);
  const dot = svgEl("circle", {
    cx: String(x),
    cy: String(y),
    r: index === activeDay ? "3.6" : "2.5",
    fill: color,
    "pointer-events": "none",
  });
  bindHover(hit, tip, textOf);
  hit.addEventListener("click", (event) => {
    event.stopPropagation();
    selectDay(index, tip, event, textOf());
  });
  svg.append(hit, dot);
}

function seriesPath(key, height, min, max) {
  const { width, padLeft, padRight, padTop, padBottom } = CHART;
  return polyline(
    READINGS.map((reading) => reading[key]),
    width,
    height,
    min,
    max,
    padLeft,
    padTop,
    padBottom,
    padRight,
  );
}

function pointXY(value, index, height, min, max) {
  const { width, padLeft, padRight, padTop, padBottom } = CHART;
  return {
    x: scaleX(index, READINGS.length, width, padLeft, padRight),
    y: scaleY(value, min, max, height, padTop, padBottom),
  };
}

function renderTemp() {
  const svg = $("tempChart");
  const tip = $("tempTip");
  const height = 150;
  prepare(svg);
  addFrame(svg, height, 10, 30, [10, 15, 20, 25, 30]);
  addStroke(svg, seriesPath("outside", height, 10, 30), COLORS.outside, { "stroke-width": "2", "stroke-dasharray": "4 4" });
  addStroke(svg, seriesPath("greenhouse", height, 10, 30), COLORS.greenhouse, { "stroke-width": "2.4" });
  addStroke(svg, seriesPath("water", height, 10, 30), COLORS.water, { "stroke-width": "2.4" });
  addDays(svg, tip, height, (reading) => `${reading.day}: water ${reading.water.toFixed(1)}°C · house ${reading.greenhouse.toFixed(1)}°C · outside ${reading.outside.toFixed(1)}°C`);
  for (const key of ["outside", "greenhouse", "water"]) {
    READINGS.forEach((reading, index) => {
      const { x, y } = pointXY(reading[key], index, height, 10, 30);
      addPoint(svg, tip, x, y, COLORS[key], index, () => `${reading.day}: ${reading[key].toFixed(1)}°C`);
    });
  }
}

function renderNitro() {
  const svg = $("nitroChart");
  const tip = $("nitroTip");
  const height = 130;
  const { padLeft, padRight, padBottom, width } = CHART;
  prepare(svg);
  addGradient(svg, "nitroFill", COLORS.nitrogen);
  addFrame(svg, height, 0, 20, [0, 5, 10, 15, 20]);
  const line = seriesPath("pulled", height, 0, 20);
  const lastX = scaleX(READINGS.length - 1, READINGS.length, width, padLeft, padRight);
  svg.append(svgEl("path", { d: `${line} L ${lastX.toFixed(1)} ${height - padBottom} L ${padLeft} ${height - padBottom} Z`, fill: "url(#nitroFill)" }));
  addStroke(svg, line, COLORS.nitrogen, { "stroke-width": "2.4" });
  addDays(svg, tip, height, (reading) => `${reading.day}: ${reading.pulled} mg/L pulled`);
  READINGS.forEach((reading, index) => {
    const { x, y } = pointXY(reading.pulled, index, height, 0, 20);
    addPoint(svg, tip, x, y, COLORS.nitrogen, index, () => `${reading.day}: ${reading.pulled} mg/L`);
  });

  const reading = READINGS[activeDay];
  if (activeDay === 0) {
    $("nitroNote").textContent = "baseline for the week";
    return;
  }
  const pct = Math.round(risePercent(READINGS[0].pulled, reading.pulled));
  const direction = pct >= 0 ? "up" : "down";
  const tail = pct >= 0
    ? " · plants working harder as bioload climbs"
    : " · plants are taking up less than the start of the week";
  setRich("nitroNote", [
    `${direction} `,
    { hl: `${Math.abs(pct)}%` },
    ` since ${READINGS[0].day}${tail}`,
  ]);
}

function renderHeadroom() {
  const reading = READINGS[activeDay];
  $("headroomVal").textContent = reading.headroom.toFixed(1);
  const pct = Math.min(100, Math.max(0, (reading.headroom / 40) * 100));
  $("headroomFill").style.width = `${pct}%`;
  $("headroomNote").textContent =
    pct < 40 ? "getting tight — consider trimming stock or adding beds" : "comfortable capacity";
}

function renderPhDo() {
  const svg = $("phDoChart");
  const tip = $("phDoTip");
  const height = 130;
  prepare(svg);
  addFrame(svg, height, 5, 9, [5, 6, 7, 8, 9]);
  addStroke(svg, seriesPath("do", height, 5, 9), COLORS.water, { "stroke-width": "2.2" });
  const phLine = polyline(
    READINGS.map((reading) => reading.ph),
    CHART.width,
    height,
    6.8,
    7.8,
    CHART.padLeft,
    CHART.padTop,
    CHART.padBottom,
    CHART.padRight,
  );
  addStroke(svg, phLine, COLORS.ph, { "stroke-width": "2.2", "stroke-dasharray": "3 3" });
  addDays(svg, tip, height, (reading) => `${reading.day}: DO ${reading.do} mg/L · pH ${reading.ph}`);
  READINGS.forEach((reading, index) => {
    const oxygen = pointXY(reading.do, index, height, 5, 9);
    const ph = pointXY(reading.ph, index, height, 6.8, 7.8);
    addPoint(svg, tip, oxygen.x, oxygen.y, COLORS.water, index, () => `${reading.day}: ${reading.do} mg/L DO`);
    addPoint(svg, tip, ph.x, ph.y, COLORS.ph, index, () => `${reading.day}: pH ${reading.ph}`);
  });
}

function renderAmmonia() {
  const svg = $("ammoniaChart");
  const tip = $("ammoniaTip");
  const height = 130;
  prepare(svg);
  addFrame(svg, height, 0, 0.4, [0, 0.1, 0.2, 0.3, 0.4], (value) => String(Math.round(value * 10) / 10));
  addStroke(svg, seriesPath("nh3raw", height, 0, 0.4), COLORS.outside, { "stroke-width": "2.2" });
  addStroke(svg, seriesPath("nh3filtered", height, 0, 0.4), COLORS.water, { "stroke-width": "2.2" });
  addDays(svg, tip, height, (reading) => `${reading.day}: ${reading.nh3raw} mg/L raw · ${reading.nh3filtered} mg/L filtered`);
  READINGS.forEach((reading, index) => {
    const raw = pointXY(reading.nh3raw, index, height, 0, 0.4);
    const filtered = pointXY(reading.nh3filtered, index, height, 0, 0.4);
    addPoint(svg, tip, raw.x, raw.y, COLORS.outside, index, () => `${reading.day}: ${reading.nh3raw} mg/L raw`);
    addPoint(svg, tip, filtered.x, filtered.y, COLORS.water, index, () => `${reading.day}: ${reading.nh3filtered} mg/L filtered`);
  });
  const reading = READINGS[activeDay];
  const removed = Math.round(removalPercent(reading.nh3raw, reading.nh3filtered));
  setRich("ammoniaNote", ["biofilter converting ~", { hl: `${removed}%` }, ` of ammonia on ${reading.day}`]);
}

function renderEc() {
  const svg = $("ecChart");
  const tip = $("ecTip");
  const height = 120;
  const { padLeft, padRight, padBottom, width } = CHART;
  prepare(svg);
  addGradient(svg, "ecFill", COLORS.outside);
  addFrame(svg, height, 650, 900, [650, 725, 800, 875]);
  const line = seriesPath("ec", height, 650, 900);
  const lastX = scaleX(READINGS.length - 1, READINGS.length, width, padLeft, padRight);
  svg.append(svgEl("path", { d: `${line} L ${lastX.toFixed(1)} ${height - padBottom} L ${padLeft} ${height - padBottom} Z`, fill: "url(#ecFill)" }));
  addStroke(svg, line, COLORS.outside, { "stroke-width": "2.2" });
  addDays(svg, tip, height, (reading) => `${reading.day}: ${reading.ec} ppm`);
  READINGS.forEach((reading, index) => {
    const { x, y } = pointXY(reading.ec, index, height, 650, 900);
    addPoint(svg, tip, x, y, COLORS.outside, index, () => `${reading.day}: ${reading.ec} ppm`);
  });
}

function renderFeed() {
  const svg = $("feedChart");
  const tip = $("feedTip");
  const height = 130;
  const { width, padLeft, padRight, padTop, padBottom } = CHART;
  prepare(svg);
  addFrame(svg, height, 0, 0.3, []);
  addDays(svg, tip, height, (reading) => `${reading.day}: ${reading.feed} kg feed · ${reading.biomass} kg biomass`);
  const barWidth = ((width - padLeft - padRight) / READINGS.length) * 0.4;
  READINGS.forEach((reading, index) => {
    const x = scaleX(index, READINGS.length, width, padLeft, padRight);
    const yTop = scaleY(reading.feed, 0, 0.3, height, padTop, padBottom);
    const yBase = scaleY(0, 0, 0.3, height, padTop, padBottom);
    const bar = svgEl("rect", {
      class: "pt",
      x: String(x - barWidth / 2),
      y: String(yTop),
      width: String(barWidth),
      height: String(Math.max(0, yBase - yTop)),
      rx: "3",
      fill: COLORS.greenhouse,
      opacity: index === activeDay ? "1" : "0.85",
    });
    const text = () => `${reading.day}: ${reading.feed} kg feed`;
    bindHover(bar, tip, text);
    bar.addEventListener("click", (event) => {
      event.stopPropagation();
      selectDay(index, tip, event, text());
    });
    svg.append(bar);
  });
  const line = polyline(
    READINGS.map((reading) => reading.biomass),
    width,
    height,
    17,
    19,
    padLeft,
    padTop,
    padBottom,
    padRight,
  );
  addStroke(svg, line, COLORS.biomass, { "stroke-width": "2.2" });
  READINGS.forEach((reading, index) => {
    const { x, y } = pointXY(reading.biomass, index, height, 17, 19);
    addPoint(svg, tip, x, y, COLORS.biomass, index, () => `${reading.day}: ${reading.biomass} kg biomass`);
  });
}

function renderSupplies() {
  const reading = READINGS[activeDay];
  const feedDays = daysOfStock(supplies.feedStockKg, feedPerDay);
  const feedPct = Math.min(100, (supplies.feedStockKg / supplies.feedBagSizeKg) * 100);
  const phPct = (supplies.phBufferMl / supplies.phBufferFullMl) * 100;
  const nutPct = (supplies.nutrientL / supplies.nutrientFullL) * 100;

  $("waterLevelVal").textContent = `${supplies.waterLevelPct}%`;
  $("waterLevelFill").style.width = `${supplies.waterLevelPct}%`;
  if (supplies.waterLevelPct < 30) {
    $("waterLevelNote").textContent = "low — check for leaks or top up soon";
  } else if (supplies.waterLevelPct < 50) {
    $("waterLevelNote").textContent = "under half — top the sump up when you can";
  } else {
    setRich("waterLevelNote", [
      "topped up automatically · normal evaporation for a ",
      { hl: `${reading.greenhouse}°C` },
      " house",
    ]);
  }

  $("feedStockVal").textContent = `${supplies.feedStockKg} kg`;
  $("feedStockFill").style.width = `${feedPct}%`;
  if (supplies.feedStockKg <= 0) {
    $("feedStockNote").textContent = "bag is empty — refill before the next feeding";
  } else {
    setRich("feedStockNote", [
      "~",
      { hl: `${feedDays} days` },
      ` left at current feed rate (${feedPerDay.toFixed(2)} kg/day avg)`,
    ]);
  }

  $("phBufferVal").textContent = `${supplies.phBufferMl} mL`;
  $("phBufferFill").style.width = `${phPct}%`;
  if (phPct < 35) $("phBufferNote").textContent = "running low — order a refill";
  else setRich("phBufferNote", [{ hl: `${phPct.toFixed(0)}%` }, " of bottle remaining"]);

  $("nutrientVal").textContent = `${supplies.nutrientL} L`;
  $("nutrientFill").style.width = `${nutPct}%`;
  if (nutPct < 35) $("nutrientNote").textContent = "running low — order a refill";
  else setRich("nutrientNote", [{ hl: `${nutPct.toFixed(0)}%` }, " of container remaining"]);

  $("water-dec").disabled = supplies.waterLevelPct <= 0;
  $("water-inc").disabled = supplies.waterLevelPct >= 100;
  $("feed-dec").disabled = supplies.feedStockKg <= 0;
  $("feed-inc").disabled = supplies.feedStockKg >= supplies.feedBagSizeKg;
  $("ph-dec").disabled = supplies.phBufferMl <= 0;
  $("ph-inc").disabled = supplies.phBufferMl >= supplies.phBufferFullMl;
  $("nutrient-dec").disabled = supplies.nutrientL <= 0;
  $("nutrient-inc").disabled = supplies.nutrientL >= supplies.nutrientFullL;
  $("resetSupplies").hidden = suppliesMatch(supplies, DEFAULT_SUPPLIES);
}

function renderStatus() {
  const reading = READINGS[activeDay];
  const report = assess(reading, supplies, feedPerDay);
  const chip = $("statusChip");
  const label = report.level === "action" ? "Needs attention" : report.level === "watch" ? "Watch" : "Steady";
  chip.textContent = label;
  chip.className = report.level === "steady" ? "chip" : `chip ${report.level}`;
  chip.setAttribute("aria-label", `Loop status: ${label}`);
  $("statusLine").textContent = steadySummary(reading);
  $("eyebrow").textContent = `Bed 2 · Ranchu loop · ${reading.day}`;

  const list = $("alerts");
  list.replaceChildren();
  if (!report.messages.length) {
    list.hidden = true;
    return;
  }
  list.hidden = false;
  for (const message of report.messages) {
    const item = document.createElement("li");
    const mark = document.createElement("span");
    mark.className = `mark ${message.level}`;
    mark.setAttribute("aria-hidden", "true");
    item.append(mark, message.text);
    list.append(item);
  }
}

function renderDay() {
  for (const button of document.querySelectorAll(".tab")) {
    const selected = Number(button.dataset.day) === activeDay;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-selected", selected ? "true" : "false");
    button.tabIndex = selected ? 0 : -1;
  }
  const reading = READINGS[activeDay];
  $("waterVal").textContent = reading.water.toFixed(1);
  $("houseVal").textContent = reading.greenhouse.toFixed(1);
  $("outsideVal").textContent = reading.outside.toFixed(1);
}

function renderAll() {
  hideTips();
  renderDay();
  renderStatus();
  renderTemp();
  renderNitro();
  renderHeadroom();
  renderPhDo();
  renderAmmonia();
  renderEc();
  renderFeed();
  renderSupplies();
}

function bind() {
  $("tabs").addEventListener("click", (event) => {
    const button = event.target.closest(".tab");
    if (!button) return;
    selectDay(Number(button.dataset.day));
  });

  $("tabs").addEventListener("keydown", (event) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    event.preventDefault();
    const direction = event.key === "ArrowRight" ? 1 : -1;
    selectDay((activeDay + direction + READINGS.length) % READINGS.length);
    $(`tab-${activeDay}`).focus();
  });

  $("supplies").addEventListener("click", (event) => {
    const button = event.target.closest("[data-supply]");
    if (!button || button.disabled) return;
    const key = button.dataset.supply;
    supplies = adjustSupply(supplies, key, Number(button.dataset.dir) * SUPPLY_STEPS[key]);
    saveSupplies();
    renderAll();
  });

  $("resetSupplies").addEventListener("click", () => {
    supplies = sanitizeSupplies(null);
    saveSupplies();
    renderAll();
  });

  document.addEventListener("pointerdown", (event) => {
    if (event.target.closest?.(".pt")) return;
    hideTips();
  });
}

bind();
renderAll();
