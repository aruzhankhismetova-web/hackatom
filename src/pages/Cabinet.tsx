import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import {
  CATEGORIES,
  DISTRICTS,
  addMinutes,
  atyrauYmd,
  byTime,
  formatMoney,
  formatTime,
  groupLabel,
  isCategoryId,
  planById,
  specialistReceives,
  type CategoryId,
  type Specialist,
} from "../model";
import { useStore, type ProfileInput } from "../store";
import { Field, Monogram, PlanCards, useTitle } from "../ui";

type Draft = {
  name: string;
  category: CategoryId;
  service: string;
  district: string;
  price: string;
  practice: string;
  bio: string;
};

const SERVICE_HINT: Record<CategoryId, string> = {
  photo: "Фотограф",
  nails: "Мастер маникюра",
  tutor: "Репетитор",
  design: "Дизайнер",
  video: "Видеограф",
  makeup: "Визажист",
};

const EXAMPLE: Draft = {
  name: "Алия Нур",
  category: "makeup",
  service: "Визажист",
  district: "Еркинкала",
  price: "9000",
  practice: "3 месяца",
  bio: "Выездной макияж по Атырау. Пока мало записей, поэтому держу окна на вечер и утро.",
};

function emptyDraft(): Draft {
  return { name: "", category: "photo", service: "", district: "Нурсая", price: "", practice: "", bio: "" };
}

function fromProfile(specialist: Specialist): Draft {
  return {
    name: specialist.name,
    category: specialist.category,
    service: specialist.service,
    district: specialist.district,
    price: String(specialist.priceFromKzt),
    practice: specialist.practice,
    bio: specialist.bio,
  };
}

function parseMoney(value: string): number | null {
  const raw = value.replace(/\s/g, "");
  if (!/^\d+$/.test(raw)) return null;
  return Number(raw);
}

export function CabinetPage() {
  useTitle("Кабинет — NEARLY");
  const store = useStore();
  const [resetArmed, setResetArmed] = useState(false);

  return (
    <main className="wrap page">
      <p className="kicker">Две стороны ленты</p>
      <h1>Кабинет</h1>
      <p className="lede">
        Здесь мастер открывает свободные часы, а клиент видит свои брони. Всё хранится в этом браузере: прототип без сервера и без оплаты.
      </p>
      <div className="cabinet-grid">
        <Supply />
        <ClientBookings />
      </div>
      <section className="section">
        <h2>Сбросить прототип</h2>
        <p className="muted">Удалит вашу анкету, открытые часы и записи в этом браузере. Учебные специалисты вернутся.</p>
        {resetArmed ? (
          <p className="page-actions">
            <button type="button" className="btn" onClick={() => store.reset()}>Да, очистить</button>
            <button type="button" className="btn btn-ghost" onClick={() => setResetArmed(false)}>Оставить</button>
          </p>
        ) : (
          <p className="page-actions">
            <button type="button" className="btn btn-ghost" onClick={() => setResetArmed(true)}>Очистить этот браузер</button>
          </p>
        )}
      </section>
    </main>
  );
}

function Supply() {
  const { profile, slots, bookings, now, createProfile, updateProfile, publishSlot, closeSlot, setPlan, cancelBooking } = useStore();
  const profileId = profile?.id ?? "";
  const [editing, setEditing] = useState(!profile);
  const [draft, setDraft] = useState<Draft>(profile ? fromProfile(profile) : emptyDraft());
  const [error, setError] = useState("");
  const [slotError, setSlotError] = useState("");
  const [slotNote, setSlotNote] = useState("");
  const [planError, setPlanError] = useState("");
  const [slotDraft, setSlotDraft] = useState({
    date: atyrauYmd(now, 1),
    time: "11:00",
    duration: "60",
    price: profile ? String(profile.priceFromKzt) : "",
    note: "",
  });

  useEffect(() => {
    if (!profileId || !profile) {
      setDraft(emptyDraft());
      setEditing(true);
      return;
    }
    setDraft(fromProfile(profile));
    setEditing(false);
    setSlotDraft((current) => ({
      ...current,
      price: current.price || String(profile.priceFromKzt),
      date: current.date || atyrauYmd(new Date(), 1),
    }));
  }, [profileId]);

  function onCategory(category: CategoryId) {
    setDraft((current) => ({
      ...current,
      category,
      service: current.service === "" || current.service === SERVICE_HINT[current.category] ? SERVICE_HINT[category] : current.service,
    }));
  }

  function saveProfile(event: FormEvent) {
    event.preventDefault();
    const price = parseMoney(draft.price);
    if (price === null) {
      setError("Цена — целое число в тенге.");
      return;
    }
    const input: ProfileInput = {
      name: draft.name,
      category: draft.category,
      service: draft.service,
      district: draft.district,
      priceFromKzt: price,
      practice: draft.practice,
      bio: draft.bio,
    };
    const result = profile ? updateProfile(input) : createProfile(input);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    setError("");
    setEditing(false);
    document.getElementById("publish")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function saveSlot(event: FormEvent) {
    event.preventDefault();
    const price = parseMoney(slotDraft.price);
    const [hour, minute] = slotDraft.time.split(":").map(Number);
    if (price === null) {
      setSlotError("Цена часа — целое число.");
      return;
    }
    const result = publishSlot({
      ymd: slotDraft.date,
      hour,
      minute,
      durationMin: Number(slotDraft.duration),
      priceKzt: price,
      note: slotDraft.note,
    });
    if (!result.ok) {
      setSlotError(result.error);
      return;
    }
    setSlotError("");
    setSlotNote("Час открыт и уже есть в ленте.");
    setSlotDraft((current) => ({ ...current, note: "" }));
  }

  const mine = profile
    ? slots.filter((slot) => slot.specialistId === profile.id && new Date(slot.startsAt).getTime() > now.getTime()).sort(byTime)
    : [];
  const limit = profile ? planById(profile.plan).openSlotLimit : 0;
  const openCount = mine.filter((slot) => slot.status === "open").length;

  return (
    <section id="supply">
      <h2>Часы специалиста</h2>
      {!profile || editing ? (
        <form className="form" onSubmit={saveProfile}>
          <p>{profile ? "Измените анкету." : "Сначала анкета, потом свободный час."}</p>
          {error ? <p className="error" role="alert">{error}</p> : null}
          <Field label="Имя">
            <input value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} maxLength={80} autoComplete="name" />
          </Field>
          <div className="fields-2">
            <Field label="Услуга">
              <select
                value={draft.category}
                onChange={(event) => {
                  if (isCategoryId(event.target.value)) onCategory(event.target.value);
                }}
              >
                {CATEGORIES.map((item) => (
                  <option key={item.id} value={item.id}>{item.label}</option>
                ))}
              </select>
            </Field>
            <Field label="Как коротко назвать">
              <input value={draft.service} onChange={(event) => setDraft({ ...draft, service: event.target.value })} maxLength={80} />
            </Field>
          </div>
          <div className="fields-2">
            <Field label="Район">
              <select value={draft.district} onChange={(event) => setDraft({ ...draft, district: event.target.value })}>
                {DISTRICTS.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </Field>
            <Field label="Цена часа, ₸">
              <input value={draft.price} onChange={(event) => setDraft({ ...draft, price: event.target.value })} inputMode="numeric" />
            </Field>
          </div>
          <Field label="Как давно практикуете" hint="Например, 6 месяцев.">
            <input value={draft.practice} onChange={(event) => setDraft({ ...draft, practice: event.target.value })} maxLength={40} />
          </Field>
          <Field label="О себе" hint="Одно предложение, до 400 знаков.">
            <textarea value={draft.bio} onChange={(event) => setDraft({ ...draft, bio: event.target.value })} maxLength={400} />
          </Field>
          <div className="row-actions">
            <button type="submit" className="btn">{profile ? "Сохранить анкету" : "Открыть анкету"}</button>
            {!profile ? (
              <button type="button" className="btn btn-ghost" onClick={() => { setDraft(EXAMPLE); setError(""); }}>
                Подставить пример
              </button>
            ) : (
              <button type="button" className="btn btn-ghost" onClick={() => { setDraft(fromProfile(profile)); setEditing(false); setError(""); }}>
                Отмена
              </button>
            )}
          </div>
        </form>
      ) : (
        <div className="profile-card">
          <Monogram name={profile.name} tone={profile.tone} />
          <div>
            <h3>{profile.name}</h3>
            <p>{profile.service} · {profile.district} · от {formatMoney(profile.priceFromKzt)}</p>
            <p className="muted">Практика {profile.practice}. Открыто {openCount} из {limit}.</p>
            <button type="button" className="prompt" onClick={() => { setDraft(fromProfile(profile)); setEditing(true); }}>Изменить анкету</button>
          </div>
        </div>
      )}

      {profile ? (
        <div className="stack" id="publish">
          <h3>Тариф</h3>
          <p className="muted">Оплата в прототипе не списывается. Тариф меняет комиссию и место часа внутри дня.</p>
          {planError ? <p className="error" role="alert">{planError}</p> : null}
          <PlanCards
            current={profile.plan}
            onPick={(plan) => {
              const result = setPlan(plan);
              setPlanError(result.ok ? "" : result.error);
            }}
          />
          <h3>Открыть час</h3>
          <form className="form" onSubmit={saveSlot}>
            {slotError ? <p className="error" role="alert">{slotError}</p> : null}
            {slotNote ? <p className="ok">{slotNote} <Link to={`/masters/${profile.id}`}>Посмотреть анкету</Link></p> : null}
            <div className="fields-2">
              <Field label="Дата">
                <input type="date" value={slotDraft.date} min={atyrauYmd(now, 0)} max={atyrauYmd(now, 90)} onChange={(event) => setSlotDraft({ ...slotDraft, date: event.target.value })} />
              </Field>
              <Field label="Начало">
                <input type="time" value={slotDraft.time} onChange={(event) => setSlotDraft({ ...slotDraft, time: event.target.value })} />
              </Field>
            </div>
            <div className="fields-2">
              <Field label="Длительность">
                <select value={slotDraft.duration} onChange={(event) => setSlotDraft({ ...slotDraft, duration: event.target.value })}>
                  <option value="30">30 мин</option>
                  <option value="60">1 час</option>
                  <option value="90">1,5 часа</option>
                  <option value="120">2 часа</option>
                  <option value="180">3 часа</option>
                  <option value="240">4 часа</option>
                </select>
              </Field>
              <Field label="Цена этого часа, ₸">
                <input value={slotDraft.price} onChange={(event) => setSlotDraft({ ...slotDraft, price: event.target.value })} inputMode="numeric" />
              </Field>
            </div>
            <Field label="Что входит">
              <input value={slotDraft.note} onChange={(event) => setSlotDraft({ ...slotDraft, note: event.target.value })} maxLength={160} placeholder="Портрет у набережной" />
            </Field>
            <button type="submit" className="btn">Опубликовать час</button>
          </form>
          <h3>Ваши часы</h3>
          {mine.length === 0 ? <p className="muted">Пока пусто. Открытый час сразу попадёт в ленту.</p> : null}
          {mine.map((slot) => {
            const booking = bookings.find((item) => item.slotId === slot.id);
            return (
              <article key={slot.id} className="booking">
                <p className="sheet-when">{groupLabel(slot.startsAt, now)} · {formatTime(slot.startsAt)}–{formatTime(addMinutes(slot.startsAt, slot.durationMin))}</p>
                <p>{slot.note} · {formatMoney(slot.priceKzt)}</p>
                {slot.status === "booked" && booking ? (
                  <>
                    <p>Занял {booking.clientName}, {booking.clientPhone}. Комиссия {formatMoney(booking.commissionKzt)}, вам остаётся {formatMoney(specialistReceives(booking.priceKzt, booking.plan))}.</p>
                    {booking.comment ? <p className="muted">{booking.comment}</p> : null}
                    <button type="button" className="btn btn-ghost btn-small" onClick={() => cancelBooking(booking.id)}>Отменить бронь</button>
                  </>
                ) : (
                  <button type="button" className="btn btn-ghost btn-small" onClick={() => closeSlot(slot.id)}>Закрыть час</button>
                )}
              </article>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}

function ClientBookings() {
  const { bookings, cancelBooking } = useStore();
  const [armed, setArmed] = useState<string | null>(null);
  return (
    <section>
      <h2>Мои записи</h2>
      <p className="muted">Брони, которые вы сделали в этом браузере. Телефон мастеру отсюда не отправляется.</p>
      {bookings.length === 0 ? (
        <div className="empty">
          <p>Записей пока нет.</p>
          <p className="page-actions"><Link to="/?focus=hours" className="btn">Найти час</Link></p>
        </div>
      ) : (
        bookings.map((booking) => (
          <article key={booking.id} className="booking">
            <p className="code-small">{booking.id}</p>
            <p><Link to={`/masters/${booking.specialistId}`}>{booking.specialistName}</Link> · {booking.service}</p>
            <p>{groupLabel(booking.startsAt)} · {formatTime(booking.startsAt)}–{formatTime(addMinutes(booking.startsAt, booking.durationMin))}</p>
            <p>{booking.note}</p>
            <p>Мастеру {formatMoney(booking.priceKzt)} · {booking.clientName}, {booking.clientPhone}</p>
            {booking.comment ? <p className="muted">{booking.comment}</p> : null}
            {armed === booking.id ? (
              <p className="row-actions">
                <button type="button" className="btn btn-small" onClick={() => cancelBooking(booking.id)}>Да, снять</button>
                <button type="button" className="btn btn-ghost btn-small" onClick={() => setArmed(null)}>Оставить</button>
              </p>
            ) : (
              <button type="button" className="btn btn-ghost btn-small" onClick={() => setArmed(booking.id)}>Отменить бронь</button>
            )}
          </article>
        ))
      )}
    </section>
  );
}
