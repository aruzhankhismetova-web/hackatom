export const CITY = "Атырау";
export const TIMEZONE = "Asia/Atyrau";

export const CATEGORIES = [
  { id: "photo", label: "Фото", aliases: ["фото", "фотограф", "фотосессия", "фотосъемка"] },
  { id: "nails", label: "Маникюр", aliases: ["маникюр", "ногти", "гель"] },
  { id: "tutor", label: "Репетитор", aliases: ["репетитор", "учитель", "ент"] },
  { id: "design", label: "Дизайн", aliases: ["дизайн", "дизайнер", "афиша"] },
  { id: "video", label: "Видео", aliases: ["видео", "видеограф", "оператор", "ролик"] },
  { id: "makeup", label: "Визаж", aliases: ["визаж", "визажист", "макияж"] },
] as const;

export type CategoryId = (typeof CATEGORIES)[number]["id"];
export type PlanId = "start" | "practice" | "nearby";
export type WhenFilter = "any" | "today" | "tomorrow" | "week";

export type Plan = {
  id: PlanId;
  name: string;
  priceKzt: number;
  rate: number;
  openSlotLimit: number;
  summary: string;
  detail: string;
};

export const PLANS: Plan[] = [
  {
    id: "start",
    name: "Старт",
    priceKzt: 0,
    rate: 0.15,
    openSlotLimit: 5,
    summary: "0 ₸ · комиссия 15%",
    detail: "До пяти открытых часов. Первые окна можно выложить, ничего не платя вперёд.",
  },
  {
    id: "practice",
    name: "Практика",
    priceKzt: 4900,
    rate: 0.1,
    openSlotLimit: 40,
    summary: "4 900 ₸/мес · комиссия 10%",
    detail: "Для тех, кто берёт заказы каждую неделю. Одновременно открыто до 40 часов.",
  },
  {
    id: "nearby",
    name: "Рядом",
    priceKzt: 9900,
    rate: 0.07,
    openSlotLimit: 80,
    summary: "9 900 ₸/мес · комиссия 7%",
    detail: "Часы стоят выше остальных внутри того же дня. Одновременно открыто до 80 часов.",
  },
];

export const DISTRICTS = [
  "Нурсая",
  "Авангард",
  "Центр",
  "Балыкши",
  "Еркинкала",
  "Акжайык",
  "Жумыскер",
  "Привокзальный",
] as const;

export type Specialist = {
  id: string;
  name: string;
  service: string;
  category: CategoryId;
  bio: string;
  district: string;
  priceFromKzt: number;
  practice: string;
  plan: PlanId;
  tone: number;
  seed: boolean;
};

export type Slot = {
  id: string;
  specialistId: string;
  startsAt: string;
  durationMin: number;
  note: string;
  priceKzt: number;
  seed: boolean;
};

export type SlotView = Slot & {
  status: "open" | "booked";
  specialist: Specialist;
};

export type Booking = {
  id: string;
  slotId: string;
  specialistId: string;
  clientName: string;
  clientPhone: string;
  comment: string;
  priceKzt: number;
  commissionKzt: number;
  plan: PlanId;
  startsAt: string;
  durationMin: number;
  note: string;
  service: string;
  specialistName: string;
  createdAt: string;
};

export const PROMPTS: { label: string; q: string; when: WhenFilter }[] = [
  { label: "Фотограф на завтра", q: "фотограф", when: "tomorrow" },
  { label: "Мастер маникюра", q: "маникюр", when: "any" },
  { label: "Репетитор", q: "репетитор", when: "any" },
  { label: "Дизайнер", q: "дизайнер", when: "any" },
  { label: "Видеограф на мероприятие", q: "видеограф мероприятие", when: "week" },
];

const STOP = new Set(["для", "или", "при", "это", "как", "что", "под", "над", "еще", "ещё"]);

export function planById(id: PlanId): Plan {
  return PLANS.find((plan) => plan.id === id) ?? PLANS[0];
}

export function categoryById(id: string) {
  return CATEGORIES.find((category) => category.id === id) ?? CATEGORIES[0];
}

export function isCategoryId(value: string): value is CategoryId {
  return CATEGORIES.some((category) => category.id === value);
}

export function isPlanId(value: string): value is PlanId {
  return value === "start" || value === "practice" || value === "nearby";
}

export function commissionOf(priceKzt: number, plan: PlanId): number {
  return Math.round(priceKzt * planById(plan).rate);
}

export function rateLabel(rate: number): string {
  return `${Math.round(rate * 100)}%`;
}

export function formatMoney(kzt: number): string {
  return `${new Intl.NumberFormat("ru-RU").format(kzt)} ₸`;
}

export function countLabel(count: number, forms: [string, string, string]): string {
  const mod100 = Math.abs(count) % 100;
  const mod10 = mod100 % 10;
  if (mod100 > 10 && mod100 < 20) return `${count} ${forms[2]}`;
  if (mod10 === 1) return `${count} ${forms[0]}`;
  if (mod10 > 1 && mod10 < 5) return `${count} ${forms[1]}`;
  return `${count} ${forms[2]}`;
}

export function specialistReceives(priceKzt: number, plan: PlanId): number {
  return priceKzt - commissionOf(priceKzt, plan);
}

export function normalizePhone(input: string): string | null {
  const digits = input.replace(/\D/g, "");
  let normalized = digits;
  if (normalized.length === 11 && (normalized.startsWith("7") || normalized.startsWith("8"))) {
    normalized = `7${normalized.slice(1)}`;
  } else if (normalized.length === 10) {
    normalized = `7${normalized}`;
  } else {
    return null;
  }
  if (!/^7\d{10}$/.test(normalized)) return null;
  return `+7 ${normalized.slice(1, 4)} ${normalized.slice(4, 7)} ${normalized.slice(7, 9)} ${normalized.slice(9, 11)}`;
}

export function initials(name: string): string {
  const letters = name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0] ?? "")
    .join("");
  return letters.toLocaleUpperCase("ru-RU") || "N";
}

export function toneFromName(name: string): number {
  return [...name].reduce((sum, char) => sum + char.charCodeAt(0), 0) % 6;
}

export function durationLabel(minutes: number): string {
  if (minutes % 60 === 0) {
    const hours = minutes / 60;
    if (hours === 1) return "1 час";
    if (hours > 1 && hours < 5) return `${hours} часа`;
    return `${hours} часов`;
  }
  if (minutes === 90) return "1,5 часа";
  if (minutes === 150) return "2,5 часа";
  return `${minutes} мин`;
}

export function atyrauYmd(now = new Date(), dayOffset = 0): string {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: TIMEZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(now);
  const year = Number(parts.find((part) => part.type === "year")?.value);
  const month = Number(parts.find((part) => part.type === "month")?.value);
  const day = Number(parts.find((part) => part.type === "day")?.value);
  const shifted = new Date(Date.UTC(year, month - 1, day + dayOffset));
  const yyyy = shifted.getUTCFullYear();
  const mm = String(shifted.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(shifted.getUTCDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export function atyrauFromParts(ymd: string, hour: number, minute: number): string {
  const [year, month, day] = ymd.split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day, hour - 5, minute, 0)).toISOString();
}

export function atyrauDate(dayOffset: number, hour: number, minute: number, now = new Date()): string {
  return atyrauFromParts(atyrauYmd(now, dayOffset), hour, minute);
}

export function dayKey(iso: string): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: TIMEZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(iso));
  return parts;
}

export function formatTime(iso: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    timeZone: TIMEZONE,
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

export function addMinutes(iso: string, minutes: number): string {
  return new Date(new Date(iso).getTime() + minutes * 60_000).toISOString();
}

function capitalize(value: string): string {
  return value.charAt(0).toLocaleUpperCase("ru-RU") + value.slice(1);
}

export function groupLabel(iso: string, now = new Date()): string {
  const key = dayKey(iso);
  const today = atyrauYmd(now, 0);
  const tomorrow = atyrauYmd(now, 1);
  const date = new Intl.DateTimeFormat("ru-RU", {
    timeZone: TIMEZONE,
    day: "numeric",
    month: "long",
  }).format(new Date(iso));
  if (key === today) return `Сегодня, ${date}`;
  if (key === tomorrow) return `Завтра, ${date}`;
  const weekday = new Intl.DateTimeFormat("ru-RU", {
    timeZone: TIMEZONE,
    weekday: "long",
  }).format(new Date(iso));
  return capitalize(`${weekday}, ${date}`);
}

export function slotIsInWhen(startsAt: string, when: WhenFilter, now: Date): boolean {
  const start = new Date(startsAt).getTime();
  if (start < now.getTime()) return false;
  if (when === "any") return true;
  const key = dayKey(startsAt);
  if (when === "today") return key === atyrauYmd(now, 0);
  if (when === "tomorrow") return key === atyrauYmd(now, 1);
  return start <= now.getTime() + 7 * 24 * 60 * 60 * 1000;
}

export function inferWhen(query: string, selected: WhenFilter): WhenFilter {
  if (selected !== "any") return selected;
  const normalized = normalizeText(query);
  if (normalized.includes("завтра")) return "tomorrow";
  if (normalized.includes("сегодня")) return "today";
  if (normalized.includes("недел")) return "week";
  return "any";
}

export function asWhen(value: string | null): WhenFilter {
  if (value === "today" || value === "tomorrow" || value === "week") return value;
  return "any";
}

function normalizeText(value: string): string {
  return value.toLowerCase().replaceAll("ё", "е");
}

export function queryTokens(query: string): string[] {
  const cleaned = normalizeText(query).replace(/на завтра|на сегодня|на этой неделе|на неделе|завтра|сегодня/g, " ");
  return cleaned.split(/[^a-zа-я0-9]+/i).filter((token) => token.length > 2 && !STOP.has(token));
}

function looseIncludes(haystack: string, token: string): boolean {
  if (haystack.includes(token)) return true;
  const stem = token.slice(0, 5);
  return stem.length >= 4 && haystack.includes(stem);
}

export function matchesSpecialist(specialist: Specialist, extra: string, query: string): boolean {
  const tokens = queryTokens(query);
  if (tokens.length === 0) return true;
  const category = categoryById(specialist.category);
  const haystack = normalizeText(
    [specialist.name, specialist.service, specialist.bio, specialist.district, specialist.practice, category.label, ...category.aliases, extra].join(" "),
  );
  return tokens.every((token) => looseIncludes(haystack, token));
}

export function byTime(a: { startsAt: string }, b: { startsAt: string }): number {
  return new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime();
}

export function orderBoard(slots: SlotView[]): SlotView[] {
  const days = new Map<string, SlotView[]>();
  const keys: string[] = [];
  for (const slot of [...slots].sort(byTime)) {
    const key = dayKey(slot.startsAt);
    if (!days.has(key)) {
      days.set(key, []);
      keys.push(key);
    }
    days.get(key)?.push(slot);
  }
  const ordered: SlotView[] = [];
  for (const key of keys) {
    const list = days.get(key) ?? [];
    ordered.push(
      ...list.filter((slot) => slot.specialist.plan === "nearby"),
      ...list.filter((slot) => slot.specialist.plan !== "nearby"),
    );
  }
  return ordered;
}

export function groupSlots(slots: SlotView[], now = new Date()): { key: string; label: string; slots: SlotView[] }[] {
  const groups: { key: string; label: string; slots: SlotView[] }[] = [];
  for (const slot of slots) {
    const key = dayKey(slot.startsAt);
    const last = groups[groups.length - 1];
    if (!last || last.key !== key) {
      groups.push({ key, label: groupLabel(slot.startsAt, now), slots: [slot] });
    } else {
      last.slots.push(slot);
    }
  }
  return groups;
}

export type SlotFilters = {
  q: string;
  when: WhenFilter;
  category: string;
  district: string;
};

export function filterSlots(slots: SlotView[], filters: SlotFilters, now: Date): SlotView[] {
  const when = inferWhen(filters.q, filters.when);
  return orderBoard(
    slots.filter((slot) => {
      if (slot.status !== "open") return false;
      if (!slotIsInWhen(slot.startsAt, when, now)) return false;
      if (filters.category !== "all" && slot.specialist.category !== filters.category) return false;
      if (filters.district !== "all" && slot.specialist.district !== filters.district) return false;
      return matchesSpecialist(slot.specialist, slot.note, filters.q);
    }),
  );
}

export function overlaps(startA: string, durationA: number, startB: string, durationB: number): boolean {
  const a0 = new Date(startA).getTime();
  const b0 = new Date(startB).getTime();
  return a0 < b0 + durationB * 60_000 && b0 < a0 + durationA * 60_000;
}

export function makeCode(): string {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const bytes = crypto.getRandomValues(new Uint8Array(4));
  let code = "NR-";
  for (const byte of bytes) code += alphabet[byte % alphabet.length];
  return code;
}

type SeedSlot = {
  id: string;
  specialistId: string;
  dayOffset: number;
  hour: number;
  minute: number;
  durationMin: number;
  note: string;
  priceKzt: number;
};

export const SEED_SPECIALISTS: Specialist[] = [
  {
    id: "aigerim",
    name: "Айгерим Садыкова",
    service: "Фотограф",
    category: "photo",
    bio: "Снимаю семьи и портреты: набережная Урала, Нурсая, иногда двор. Отдаю 25–40 кадров на следующий день.",
    district: "Нурсая",
    priceFromKzt: 12000,
    practice: "1 год 2 месяца",
    plan: "practice",
    tone: 0,
    seed: true,
  },
  {
    id: "dinara",
    name: "Динара Кенже",
    service: "Мастер маникюра",
    category: "nails",
    bio: "Одно кресло дома в Авангарде. Гель-лак, укрепление, спокойный цвет. Беру одного человека за сеанс.",
    district: "Авангард",
    priceFromKzt: 7000,
    practice: "9 месяцев",
    plan: "start",
    tone: 2,
    seed: true,
  },
  {
    id: "erlan",
    name: "Ерлан Мусин",
    service: "Репетитор по математике",
    category: "tutor",
    bio: "9–11 класс и ЕНТ. Объясняю коротко и оставляю три задачи до следующего раза. Онлайн или у вас в Акжайыке.",
    district: "Акжайык",
    priceFromKzt: 5000,
    practice: "7 месяцев",
    plan: "start",
    tone: 3,
    seed: true,
  },
  {
    id: "asel",
    name: "Асель Тлегенова",
    service: "Графический дизайнер",
    category: "design",
    bio: "Афиша, меню или пачка сторис за один созвон. Работаю из центра, файлы отдаю в тот же день.",
    district: "Центр",
    priceFromKzt: 8000,
    practice: "11 месяцев",
    plan: "practice",
    tone: 4,
    seed: true,
  },
  {
    id: "marat",
    name: "Марат Искаков",
    service: "Видеограф",
    category: "video",
    bio: "Один оператор на мероприятие: той, выпускной, корпоратив. После съёмки собираю ролик на одну-две минуты.",
    district: "Привокзальный",
    priceFromKzt: 25000,
    practice: "1 год 5 месяцев",
    plan: "nearby",
    tone: 1,
    seed: true,
  },
  {
    id: "kamila",
    name: "Камила Омарова",
    service: "Визажист",
    category: "makeup",
    bio: "Макияж на съёмку и на выход. Выезжаю по Атырау, кисти и расходники уже в цене.",
    district: "Еркинкала",
    priceFromKzt: 10000,
    practice: "6 месяцев",
    plan: "start",
    tone: 5,
    seed: true,
  },
  {
    id: "nursulu",
    name: "Нурсулу Бек",
    service: "Репетитор английского",
    category: "tutor",
    bio: "Разговорный с нуля и для тех, кто застрял. Без длинных домашних. Жумыскер или онлайн.",
    district: "Жумыскер",
    priceFromKzt: 4500,
    practice: "4 месяца",
    plan: "start",
    tone: 3,
    seed: true,
  },
  {
    id: "bauyrzhan",
    name: "Бауыржан Али",
    service: "Предметный фотограф",
    category: "photo",
    bio: "Свет и фон на Сатпаева. За час снимаю партию товара для карточек и соцсетей.",
    district: "Центр",
    priceFromKzt: 9000,
    practice: "8 месяцев",
    plan: "practice",
    tone: 0,
    seed: true,
  },
  {
    id: "sabina",
    name: "Сабина Рахим",
    service: "Видеограф коротких роликов",
    category: "video",
    bio: "Приезжаю к мастеру или в магазин, снимаю короткий ролик и отдаю черновик в тот же день.",
    district: "Балыкши",
    priceFromKzt: 15000,
    practice: "5 месяцев",
    plan: "start",
    tone: 2,
    seed: true,
  },
];

const SEED_SLOTS: SeedSlot[] = [
  { id: "aigerim-1", specialistId: "aigerim", dayOffset: 1, hour: 11, minute: 0, durationMin: 120, note: "Прогулка, набережная Урала", priceKzt: 12000 },
  { id: "aigerim-2", specialistId: "aigerim", dayOffset: 3, hour: 16, minute: 0, durationMin: 60, note: "Портрет в Нурсае", priceKzt: 12000 },
  { id: "dinara-1", specialistId: "dinara", dayOffset: 0, hour: 17, minute: 30, durationMin: 90, note: "Покрытие гель-лаком", priceKzt: 7000 },
  { id: "dinara-2", specialistId: "dinara", dayOffset: 1, hour: 12, minute: 0, durationMin: 90, note: "Маникюр и покрытие", priceKzt: 7000 },
  { id: "dinara-3", specialistId: "dinara", dayOffset: 2, hour: 15, minute: 0, durationMin: 90, note: "Снятие и новое покрытие", priceKzt: 7000 },
  { id: "erlan-1", specialistId: "erlan", dayOffset: 1, hour: 18, minute: 0, durationMin: 60, note: "Алгебра, 10 класс", priceKzt: 5000 },
  { id: "erlan-2", specialistId: "erlan", dayOffset: 2, hour: 18, minute: 0, durationMin: 60, note: "Разбор пробника ЕНТ", priceKzt: 5000 },
  { id: "erlan-3", specialistId: "erlan", dayOffset: 4, hour: 11, minute: 0, durationMin: 60, note: "Геометрия с нуля", priceKzt: 5000 },
  { id: "asel-1", specialistId: "asel", dayOffset: 0, hour: 19, minute: 30, durationMin: 60, note: "Сторис для кафе", priceKzt: 8000 },
  { id: "asel-2", specialistId: "asel", dayOffset: 1, hour: 10, minute: 30, durationMin: 90, note: "Афиша на выходные", priceKzt: 12000 },
  { id: "marat-1", specialistId: "marat", dayOffset: 2, hour: 15, minute: 0, durationMin: 180, note: "Съёмка мероприятия, 3 часа", priceKzt: 35000 },
  { id: "marat-2", specialistId: "marat", dayOffset: 5, hour: 12, minute: 0, durationMin: 120, note: "Короткий выезд, 2 часа", priceKzt: 25000 },
  { id: "kamila-1", specialistId: "kamila", dayOffset: 1, hour: 9, minute: 0, durationMin: 75, note: "Макияж на съёмку", priceKzt: 10000 },
  { id: "kamila-2", specialistId: "kamila", dayOffset: 3, hour: 8, minute: 30, durationMin: 90, note: "Образ на выход", priceKzt: 12000 },
  { id: "nursulu-1", specialistId: "nursulu", dayOffset: 0, hour: 20, minute: 0, durationMin: 60, note: "Разговор, уровень A2", priceKzt: 4500 },
  { id: "nursulu-2", specialistId: "nursulu", dayOffset: 2, hour: 17, minute: 30, durationMin: 60, note: "Времена без зубрёжки", priceKzt: 4500 },
  { id: "bauyrzhan-1", specialistId: "bauyrzhan", dayOffset: 1, hour: 14, minute: 0, durationMin: 60, note: "Партия из 10–15 предметов", priceKzt: 9000 },
  { id: "bauyrzhan-2", specialistId: "bauyrzhan", dayOffset: 2, hour: 14, minute: 0, durationMin: 120, note: "Съёмка для магазина", priceKzt: 16000 },
  { id: "sabina-1", specialistId: "sabina", dayOffset: 1, hour: 13, minute: 0, durationMin: 60, note: "Ролик для мастера", priceKzt: 15000 },
  { id: "sabina-2", specialistId: "sabina", dayOffset: 4, hour: 11, minute: 0, durationMin: 90, note: "Три коротких ролика", priceKzt: 18000 },
];

export function materializeSeedSlots(now = new Date()): Slot[] {
  const earliest = now.getTime() + 15 * 60_000;
  return SEED_SLOTS.map((template) => {
    let startsAt = atyrauDate(template.dayOffset, template.hour, template.minute, now);
    while (new Date(startsAt).getTime() < earliest) {
      startsAt = new Date(new Date(startsAt).getTime() + 24 * 60 * 60 * 1000).toISOString();
    }
    return {
      id: template.id,
      specialistId: template.specialistId,
      startsAt,
      durationMin: template.durationMin,
      note: template.note,
      priceKzt: template.priceKzt,
      seed: true,
    };
  });
}
