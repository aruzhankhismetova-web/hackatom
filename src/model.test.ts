import { describe, expect, it } from "vitest";
import {
  SEED_SPECIALISTS,
  atyrauFromParts,
  commissionOf,
  countLabel,
  dayKey,
  filterSlots,
  inferWhen,
  materializeSeedSlots,
  matchesSpecialist,
  normalizePhone,
  orderBoard,
  queryTokens,
  type SlotView,
  type Specialist,
} from "./model";

const NOW = new Date("2026-11-09T11:52:00.000Z");

describe("Atyrau time", () => {
  it("stores 11:00 in Atyrau as 06:00 UTC", () => {
    expect(atyrauFromParts("2026-11-10", 11, 0)).toBe("2026-11-10T06:00:00.000Z");
    expect(dayKey("2026-11-10T06:00:00.000Z")).toBe("2026-11-10");
  });

  it("keeps today's evening hours when it is still afternoon in Atyrau", () => {
    const slots = materializeSeedSlots(NOW);
    expect(slots.find((slot) => slot.id === "aigerim-1")?.startsAt).toBe("2026-11-10T06:00:00.000Z");
    expect(slots.find((slot) => slot.id === "dinara-1")?.startsAt).toBe("2026-11-09T12:30:00.000Z");
    expect(slots.every((slot) => new Date(slot.startsAt).getTime() >= NOW.getTime() + 15 * 60_000)).toBe(true);
    expect(slots.some((slot) => dayKey(slot.startsAt) === "2026-11-09")).toBe(true);
  });
});

describe("search", () => {
  const views: SlotView[] = materializeSeedSlots(NOW).map((slot) => ({
    ...slot,
    status: "open",
    specialist: SEED_SPECIALISTS.find((person) => person.id === slot.specialistId) as Specialist,
  }));

  it("finds a photographer for tomorrow", () => {
    const result = filterSlots(views, { q: "фотограф на завтра", when: "any", category: "all", district: "all" }, NOW);
    expect(result.length).toBeGreaterThan(0);
    expect(result.every((slot) => slot.specialist.category === "photo")).toBe(true);
    expect(result.every((slot) => dayKey(slot.startsAt) === "2026-11-10")).toBe(true);
    expect(result.map((slot) => slot.id)).toContain("aigerim-1");
  });

  it("keeps the event videographer and leaves short-form video out", () => {
    const result = filterSlots(views, { q: "видеограф мероприятие", when: "week", category: "all", district: "all" }, NOW);
    expect(new Set(result.map((slot) => slot.specialistId))).toEqual(new Set(["marat"]));
  });

  it("stems client wording", () => {
    expect(queryTokens("Фотограф на завтра")).toEqual(["фотограф"]);
    expect(inferWhen("репетитор на завтра", "any")).toBe("tomorrow");
    expect(inferWhen("репетитор на завтра", "today")).toBe("today");
    const tutor = SEED_SPECIALISTS.find((person) => person.id === "erlan") as Specialist;
    expect(matchesSpecialist(tutor, "", "репетитора")).toBe(true);
  });
});

describe("money and phone", () => {
  it("takes the plan commission from the specialist price", () => {
    expect(commissionOf(12000, "practice")).toBe(1200);
    expect(commissionOf(7000, "start")).toBe(1050);
    expect(commissionOf(35000, "nearby")).toBe(2450);
  });

  it("normalizes Kazakhstan numbers", () => {
    expect(normalizePhone("+7 (701) 123-45-67")).toBe("+7 701 123 45 67");
    expect(normalizePhone("87011234567")).toBe("+7 701 123 45 67");
    expect(normalizePhone("7011234567")).toBe("+7 701 123 45 67");
    expect(normalizePhone("123")).toBeNull();
  });

  it("pluralizes Russian counts", () => {
    expect(countLabel(1, ["час", "часа", "часов"])).toBe("1 час");
    expect(countLabel(2, ["час", "часа", "часов"])).toBe("2 часа");
    expect(countLabel(5, ["час", "часа", "часов"])).toBe("5 часов");
    expect(countLabel(21, ["час", "часа", "часов"])).toBe("21 час");
  });
});

describe("board order", () => {
  it("lifts the nearby plan inside a day without jumping over earlier days", () => {
    const specialist = (id: string, plan: Specialist["plan"]): Specialist => ({
      id,
      name: id,
      service: "Тест",
      category: "photo",
      bio: "Короткое описание для проверки сортировки ленты.",
      district: "Центр",
      priceFromKzt: 10000,
      practice: "1 месяц",
      plan,
      tone: 1,
      seed: false,
    });
    const slot = (id: string, person: Specialist, ymd: string, hour: number): SlotView => ({
      id,
      specialistId: person.id,
      startsAt: atyrauFromParts(ymd, hour, 0),
      durationMin: 60,
      note: "час",
      priceKzt: 10000,
      seed: false,
      status: "open",
      specialist: person,
    });
    const early = specialist("early", "start");
    const paid = specialist("paid", "nearby");
    const morning = specialist("morning", "start");
    const ordered = orderBoard([
      slot("late-paid", paid, "2026-11-10", 18),
      slot("tomorrow-morning", morning, "2026-11-10", 10),
      slot("today", early, "2026-11-09", 19),
    ]);
    expect(ordered.map((item) => item.id)).toEqual(["today", "late-paid", "tomorrow-morning"]);
  });
});
