import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import {
  DISTRICTS,
  SEED_SPECIALISTS,
  atyrauFromParts,
  commissionOf,
  dayKey,
  isCategoryId,
  isPlanId,
  makeCode,
  materializeSeedSlots,
  normalizePhone,
  overlaps,
  planById,
  toneFromName,
  type Booking,
  type CategoryId,
  type PlanId,
  type Slot,
  type SlotView,
  type Specialist,
} from "./model";

const STORAGE_KEY = "nearly-atyrau-v1";
const DURATIONS = new Set([30, 60, 75, 90, 120, 150, 180, 240]);

export type Overlay = {
  specialists: Specialist[];
  slots: Slot[];
  bookedSlotIds: string[];
  closedSlotIds: string[];
  bookings: Booking[];
  profileId: string | null;
  plans: Partial<Record<string, PlanId>>;
  lastClient: { name: string; phone: string } | null;
};

export type ProfileInput = {
  name: string;
  category: CategoryId;
  service: string;
  district: string;
  priceFromKzt: number;
  practice: string;
  bio: string;
};

export type SlotInput = {
  ymd: string;
  hour: number;
  minute: number;
  durationMin: number;
  priceKzt: number;
  note: string;
};

type Result<T> = { ok: true; value: T } | { ok: false; error: string };

type StoreValue = {
  specialists: Specialist[];
  slots: SlotView[];
  openSlots: SlotView[];
  bookings: Booking[];
  profile: Specialist | null;
  now: Date;
  bookingSlotId: string | null;
  lastClient: { name: string; phone: string } | null;
  openBooking: (slotId: string) => void;
  closeBooking: () => void;
  book: (slotId: string, input: { name: string; phone: string; comment: string }) => Result<Booking>;
  createProfile: (input: ProfileInput) => Result<Specialist>;
  updateProfile: (input: ProfileInput) => Result<Specialist>;
  publishSlot: (input: SlotInput) => Result<Slot>;
  closeSlot: (slotId: string) => Result<null>;
  cancelBooking: (bookingId: string) => Result<null>;
  setPlan: (plan: PlanId) => Result<null>;
  reset: () => void;
};

const StoreContext = createContext<StoreValue | null>(null);

export function useStore(): StoreValue {
  const value = useContext(StoreContext);
  if (!value) throw new Error("Store is missing");
  return value;
}

function emptyOverlay(): Overlay {
  return {
    specialists: [],
    slots: [],
    bookedSlotIds: [],
    closedSlotIds: [],
    bookings: [],
    profileId: null,
    plans: {},
    lastClient: null,
  };
}

function asText(value: unknown, max: number): string {
  if (typeof value !== "string") return "";
  return value.trim().slice(0, max);
}

function sanitize(raw: unknown): Overlay {
  const empty = emptyOverlay();
  if (!raw || typeof raw !== "object") return empty;
  const data = raw as Partial<Overlay>;
  const specialists = Array.isArray(data.specialists)
    ? data.specialists.flatMap((item) => {
        if (!item || typeof item !== "object") return [];
        const source = item as Partial<Specialist>;
        if (!isCategoryId(String(source.category ?? "")) || !isPlanId(String(source.plan ?? ""))) return [];
        if (!(DISTRICTS as readonly string[]).includes(String(source.district ?? ""))) return [];
        const name = asText(source.name, 80);
        const service = asText(source.service, 80);
        const bio = asText(source.bio, 400);
        const practice = asText(source.practice, 40);
        const price = source.priceFromKzt;
        if (!name || !service || !bio || !practice || typeof price !== "number") return [];
        const specialist: Specialist = {
          id: asText(source.id, 80) || `local-${crypto.randomUUID()}`,
          name,
          service,
          category: source.category as CategoryId,
          bio,
          district: String(source.district),
          priceFromKzt: Math.round(price),
          practice,
          plan: source.plan as PlanId,
          tone: typeof source.tone === "number" ? source.tone % 6 : toneFromName(name),
          seed: false,
        };
        return [specialist];
      }).slice(0, 20)
    : [];
  const slots = Array.isArray(data.slots)
    ? data.slots.flatMap((item) => {
        if (!item || typeof item !== "object") return [];
        const source = item as Partial<Slot>;
        if (typeof source.startsAt !== "string" || Number.isNaN(new Date(source.startsAt).getTime())) return [];
        if (typeof source.durationMin !== "number" || typeof source.priceKzt !== "number") return [];
        const slot: Slot = {
          id: asText(source.id, 80) || `slot-${crypto.randomUUID()}`,
          specialistId: asText(source.specialistId, 80),
          startsAt: new Date(source.startsAt).toISOString(),
          durationMin: source.durationMin,
          note: asText(source.note, 160),
          priceKzt: Math.round(source.priceKzt),
          seed: false,
        };
        return slot.specialistId ? [slot] : [];
      }).slice(0, 80)
    : [];
  const bookings = Array.isArray(data.bookings)
    ? data.bookings.flatMap((item) => {
        if (!item || typeof item !== "object") return [];
        const source = item as Partial<Booking>;
        if (!isPlanId(String(source.plan ?? ""))) return [];
        const booking: Booking = {
          id: asText(source.id, 20),
          slotId: asText(source.slotId, 80),
          specialistId: asText(source.specialistId, 80),
          clientName: asText(source.clientName, 80),
          clientPhone: asText(source.clientPhone, 20),
          comment: asText(source.comment, 300),
          priceKzt: typeof source.priceKzt === "number" ? Math.round(source.priceKzt) : 0,
          commissionKzt: typeof source.commissionKzt === "number" ? Math.round(source.commissionKzt) : 0,
          plan: source.plan as PlanId,
          startsAt: typeof source.startsAt === "string" ? source.startsAt : "",
          durationMin: typeof source.durationMin === "number" ? source.durationMin : 60,
          note: asText(source.note, 160),
          service: asText(source.service, 80),
          specialistName: asText(source.specialistName, 80),
          createdAt: typeof source.createdAt === "string" ? source.createdAt : new Date().toISOString(),
        };
        return booking.id && booking.slotId ? [booking] : [];
      }).slice(0, 100)
    : [];
  const plans: Overlay["plans"] = {};
  if (data.plans && typeof data.plans === "object") {
    for (const [id, plan] of Object.entries(data.plans)) {
      if (isPlanId(String(plan))) plans[id] = plan as PlanId;
    }
  }
  const ids = (value: unknown) => (Array.isArray(value) ? value.filter((item): item is string => typeof item === "string").slice(0, 200) : []);
  const last = data.lastClient;
  return {
    specialists,
    slots,
    bookedSlotIds: ids(data.bookedSlotIds),
    closedSlotIds: ids(data.closedSlotIds),
    bookings,
    profileId: asText(data.profileId, 80) || null,
    plans,
    lastClient: last && typeof last === "object" && asText(last.name, 80) ? { name: asText(last.name, 80), phone: asText(last.phone, 20) } : null,
  };
}

function load(): Overlay {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyOverlay();
    return sanitize(JSON.parse(raw));
  } catch {
    return emptyOverlay();
  }
}

function build(overlay: Overlay, now: Date): { specialists: Specialist[]; slots: SlotView[] } {
  const specialists = [...SEED_SPECIALISTS, ...overlay.specialists].map((specialist) => {
    const plan = overlay.plans[specialist.id];
    return plan ? { ...specialist, plan } : specialist;
  });
  const byId = new Map(specialists.map((specialist) => [specialist.id, specialist]));
  const booked = new Set(overlay.bookedSlotIds);
  const closed = new Set(overlay.closedSlotIds);
  const slots = [...materializeSeedSlots(now), ...overlay.slots].flatMap((slot) => {
    const specialist = byId.get(slot.specialistId);
    if (!specialist || closed.has(slot.id)) return [];
    return [{ ...slot, status: booked.has(slot.id) ? ("booked" as const) : ("open" as const), specialist }];
  });
  return { specialists, slots };
}

function profileError(input: ProfileInput): string | null {
  if (input.name.trim().length < 2 || input.name.trim().length > 80) return "Напишите имя, как к вам обращаться.";
  if (!isCategoryId(input.category)) return "Выберите услугу.";
  if (input.service.trim().length < 2) return "Коротко назовите услугу.";
  if (!(DISTRICTS as readonly string[]).includes(input.district)) return "Выберите район Атырау.";
  if (!Number.isInteger(input.priceFromKzt) || input.priceFromKzt < 1000 || input.priceFromKzt > 500_000) {
    return "Цена — целое число от 1 000 до 500 000 ₸.";
  }
  if (input.practice.trim().length < 2) return "Напишите, как давно практикуете.";
  if (input.bio.trim().length < 20) return "В описании нужно хотя бы одно предложение.";
  if (input.bio.trim().length > 400) return "Описание короче 400 знаков.";
  return null;
}

function toProfile(id: string, input: ProfileInput, plan: PlanId): Specialist {
  return {
    id,
    name: input.name.trim(),
    service: input.service.trim(),
    category: input.category,
    bio: input.bio.trim(),
    district: input.district,
    priceFromKzt: input.priceFromKzt,
    practice: input.practice.trim(),
    plan,
    tone: toneFromName(input.name),
    seed: false,
  };
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const [overlay, setOverlay] = useState<Overlay>(() => load());
  const [now, setNow] = useState(() => new Date());
  const [bookingSlotId, setBookingSlotId] = useState<string | null>(null);
  const overlayRef = useRef(overlay);
  overlayRef.current = overlay;

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 30_000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(overlay));
    } catch {
      // The prototype still works for this tab if storage is unavailable.
    }
  }, [overlay]);

  function commit(next: Overlay) {
    overlayRef.current = next;
    setOverlay(next);
  }

  const { specialists, slots } = build(overlay, now);
  const openSlots = slots.filter((slot) => slot.status === "open" && new Date(slot.startsAt).getTime() > now.getTime());
  const profile = specialists.find((specialist) => specialist.id === overlay.profileId) ?? null;

  const value: StoreValue = {
    specialists,
    slots,
    openSlots,
    bookings: overlay.bookings,
    profile,
    now,
    bookingSlotId,
    lastClient: overlay.lastClient,
    openBooking(slotId) {
      const current = build(overlayRef.current, new Date());
      if (current.slots.some((slot) => slot.id === slotId && slot.status === "open")) setBookingSlotId(slotId);
    },
    closeBooking() {
      setBookingSlotId(null);
    },
    book(slotId, input) {
      const current = build(overlayRef.current, new Date());
      const slot = current.slots.find((item) => item.id === slotId);
      if (!slot || slot.status !== "open" || new Date(slot.startsAt).getTime() <= Date.now()) {
        return { ok: false, error: "Этот час уже недоступен." };
      }
      const name = input.name.trim();
      const comment = input.comment.trim();
      if (name.length < 2 || name.length > 80) return { ok: false, error: "Напишите, как к вам обращаться." };
      if (comment.length > 300) return { ok: false, error: "Комментарий короче 300 знаков." };
      const normalized = normalizePhone(input.phone);
      if (!normalized) return { ok: false, error: "Нужен телефон в формате +7 701 123 45 67." };
      let code = makeCode();
      const used = new Set(overlayRef.current.bookings.map((item) => item.id));
      while (used.has(code)) code = makeCode();
      const booking: Booking = {
        id: code,
        slotId,
        specialistId: slot.specialistId,
        clientName: name,
        clientPhone: normalized,
        comment,
        priceKzt: slot.priceKzt,
        commissionKzt: commissionOf(slot.priceKzt, slot.specialist.plan),
        plan: slot.specialist.plan,
        startsAt: slot.startsAt,
        durationMin: slot.durationMin,
        note: slot.note,
        service: slot.specialist.service,
        specialistName: slot.specialist.name,
        createdAt: new Date().toISOString(),
      };
      commit({
        ...overlayRef.current,
        bookings: [booking, ...overlayRef.current.bookings].slice(0, 100),
        bookedSlotIds: [...overlayRef.current.bookedSlotIds, slotId],
        lastClient: { name, phone: normalized },
      });
      return { ok: true, value: booking };
    },
    createProfile(input) {
      const error = profileError(input);
      if (error) return { ok: false, error };
      const existing = build(overlayRef.current, new Date()).specialists.find((item) => item.id === overlayRef.current.profileId);
      if (existing && !existing.seed) return { ok: false, error: "Анкета уже открыта. Её можно изменить ниже." };
      const specialist = toProfile(`local-${crypto.randomUUID()}`, input, "start");
      commit({
        ...overlayRef.current,
        specialists: [...overlayRef.current.specialists, specialist].slice(0, 20),
        profileId: specialist.id,
      });
      return { ok: true, value: specialist };
    },
    updateProfile(input) {
      const error = profileError(input);
      if (error) return { ok: false, error };
      const id = overlayRef.current.profileId;
      const current = overlayRef.current.specialists.find((item) => item.id === id);
      if (!id || !current) return { ok: false, error: "Сначала откройте анкету." };
      const specialist = { ...toProfile(id, input, current.plan), tone: current.tone };
      commit({
        ...overlayRef.current,
        specialists: overlayRef.current.specialists.map((item) => (item.id === id ? specialist : item)),
      });
      return { ok: true, value: specialist };
    },
    publishSlot(input) {
      const id = overlayRef.current.profileId;
      const current = build(overlayRef.current, new Date());
      const specialist = current.specialists.find((item) => item.id === id);
      if (!specialist || specialist.seed) return { ok: false, error: "Сначала откройте свою анкету." };
      if (!/^\d{4}-\d{2}-\d{2}$/.test(input.ymd)) return { ok: false, error: "Выберите дату." };
      if (!Number.isInteger(input.hour) || input.hour < 0 || input.hour > 23 || !Number.isInteger(input.minute) || input.minute < 0 || input.minute > 59) {
        return { ok: false, error: "Проверьте время." };
      }
      if (!DURATIONS.has(input.durationMin)) return { ok: false, error: "Выберите длительность." };
      if (!Number.isInteger(input.priceKzt) || input.priceKzt < 1000 || input.priceKzt > 500_000) {
        return { ok: false, error: "Цена часа — от 1 000 до 500 000 ₸." };
      }
      const note = input.note.trim();
      if (note.length < 3 || note.length > 160) return { ok: false, error: "Напишите, что входит в этот час." };
      const startsAt = atyrauFromParts(input.ymd, input.hour, input.minute);
      if (Number.isNaN(new Date(startsAt).getTime()) || dayKey(startsAt) !== input.ymd) return { ok: false, error: "Такой даты нет." };
      if (new Date(startsAt).getTime() < Date.now() + 15 * 60_000) return { ok: false, error: "Этот час уже слишком близко. Откройте время хотя бы на 15 минут вперёд." };
      const ownOpen = current.slots.filter((slot) => slot.specialistId === specialist.id && slot.status === "open" && new Date(slot.startsAt).getTime() > Date.now());
      if (ownOpen.length >= planById(specialist.plan).openSlotLimit) {
        const plan = planById(specialist.plan);
        return { ok: false, error: `На тарифе «${plan.name}» можно держать ${plan.openSlotLimit} открытых часов. Закройте лишний или смените тариф.` };
      }
      if (ownOpen.some((slot) => overlaps(slot.startsAt, slot.durationMin, startsAt, input.durationMin))) {
        return { ok: false, error: "Это время пересекается с уже открытым часом." };
      }
      const slot: Slot = {
        id: `slot-${crypto.randomUUID()}`,
        specialistId: specialist.id,
        startsAt,
        durationMin: input.durationMin,
        note,
        priceKzt: input.priceKzt,
        seed: false,
      };
      commit({ ...overlayRef.current, slots: [...overlayRef.current.slots, slot].slice(0, 80) });
      return { ok: true, value: slot };
    },
    closeSlot(slotId) {
      const current = build(overlayRef.current, new Date());
      const slot = current.slots.find((item) => item.id === slotId && item.specialistId === overlayRef.current.profileId);
      if (!slot) return { ok: false, error: "Этот час не найден в вашей анкете." };
      if (slot.status === "booked") return { ok: false, error: "Сначала отмените бронь на этот час." };
      if (slot.seed) {
        commit({ ...overlayRef.current, closedSlotIds: [...overlayRef.current.closedSlotIds, slotId] });
      } else {
        commit({ ...overlayRef.current, slots: overlayRef.current.slots.filter((item) => item.id !== slotId) });
      }
      return { ok: true, value: null };
    },
    cancelBooking(bookingId) {
      const booking = overlayRef.current.bookings.find((item) => item.id === bookingId);
      if (!booking) return { ok: false, error: "Запись не найдена." };
      commit({
        ...overlayRef.current,
        bookings: overlayRef.current.bookings.filter((item) => item.id !== bookingId),
        bookedSlotIds: overlayRef.current.bookedSlotIds.filter((id) => id !== booking.slotId),
      });
      return { ok: true, value: null };
    },
    setPlan(plan) {
      const id = overlayRef.current.profileId;
      if (!id || !overlayRef.current.specialists.some((item) => item.id === id)) {
        return { ok: false, error: "Сначала откройте анкету." };
      }
      commit({ ...overlayRef.current, plans: { ...overlayRef.current.plans, [id]: plan } });
      return { ok: true, value: null };
    },
    reset() {
      commit(emptyOverlay());
      setBookingSlotId(null);
    },
  };

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}
