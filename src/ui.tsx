import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import {
  PLANS,
  addMinutes,
  durationLabel,
  formatMoney,
  formatTime,
  groupLabel,
  initials,
  rateLabel,
  type PlanId,
  type SlotView,
} from "./model";
import { useStore } from "./store";

export function useTitle(title: string) {
  useEffect(() => {
    document.title = title;
  }, [title]);
}

export function Monogram({ name, tone, size = "md" }: { name: string; tone: number; size?: "md" | "lg" }) {
  return (
    <span className={`mono mono-${size} tone-${tone % 6}`} aria-hidden="true">
      {initials(name)}
    </span>
  );
}

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint ? <small>{hint}</small> : null}
    </label>
  );
}

function Header() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  useEffect(() => {
    setOpen(false);
  }, [location.pathname, location.search]);

  return (
    <header className="header">
      <div className="wrap header-inner">
        <div className="brand">
          <Link to="/" className="brand-link">
            <span className="mark" aria-hidden="true" />
            <span className="logo-type">NEARLY</span>
          </Link>
          <span className="city">Атырау</span>
        </div>
        <button
          type="button"
          className="menu-btn"
          aria-expanded={open}
          aria-controls="site-nav"
          onClick={() => setOpen((value) => !value)}
        >
          {open ? "Закрыть" : "Меню"}
        </button>
        <nav id="site-nav" className={open ? "nav open" : "nav"}>
          <Link to="/?focus=hours" className="nav-link">Свободные часы</Link>
          <NavLink to="/masters" className={({ isActive }) => (isActive ? "nav-link on" : "nav-link")}>Специалисты</NavLink>
          <NavLink to="/pricing" className={({ isActive }) => (isActive ? "nav-link on" : "nav-link")}>Тарифы</NavLink>
          <NavLink to="/cabinet" className={({ isActive }) => (isActive ? "nav-link on" : "nav-link")}>Кабинет</NavLink>
        </nav>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <div className="wrap footer-grid">
        <div>
          <p className="logo-type">NEARLY</p>
          <p>Найди специалиста рядом. Старт — один город, Атырау.</p>
        </div>
        <div>
          <p>Комиссия с брони и подписка для специалистов.</p>
          <p>Клиент платит мастеру цену из ленты.</p>
        </div>
        <p className="muted">Учебные анкеты. Записи прототипа остаются в этом браузере.</p>
      </div>
    </footer>
  );
}

export function Shell({ children }: { children: ReactNode }) {
  return (
    <>
      <button type="button" className="skip" onClick={() => document.getElementById("content")?.focus()}>
        К содержанию
      </button>
      <Header />
      <div id="content" tabIndex={-1}>{children}</div>
      <Footer />
      <BookDialog />
    </>
  );
}

export function SlotRow({ slot }: { slot: SlotView }) {
  const { openBooking } = useStore();
  const end = addMinutes(slot.startsAt, slot.durationMin);
  const time = `${formatTime(slot.startsAt)}–${formatTime(end)}`;
  return (
    <article className="slot">
      <div className="slot-when">
        <p className="slot-time">{time}</p>
        <p className="muted">{durationLabel(slot.durationMin)}</p>
      </div>
      <div className="slot-who">
        <Monogram name={slot.specialist.name} tone={slot.specialist.tone} />
        <div>
          <h3>
            <Link to={`/masters/${slot.specialist.id}`}>{slot.specialist.name}</Link>
          </h3>
          <p>{slot.note}</p>
        </div>
      </div>
      <div className="slot-meta">
        <p>{slot.specialist.service}</p>
        <p>{slot.specialist.district}</p>
        {slot.specialist.plan === "nearby" ? <p className="lift">Выше в ленте</p> : null}
      </div>
      <div className="slot-book">
        <p className="price">{formatMoney(slot.priceKzt)}</p>
        <p className="muted price-note">мастеру</p>
        <button
          type="button"
          className="btn"
          onClick={() => openBooking(slot.id)}
          aria-label={`Забронировать ${slot.specialist.name}, ${time}`}
        >
          Забронировать
        </button>
      </div>
    </article>
  );
}

export function PlanCards({ current, onPick }: { current?: PlanId; onPick?: (id: PlanId) => void }) {
  return (
    <div className="plans">
      {PLANS.map((plan) => {
        const className = ["plan", !onPick && plan.id === "practice" ? "featured" : "", current === plan.id ? "current" : ""].filter(Boolean).join(" ");
        const inner = (
          <>
            <p className="plan-name">{plan.name}</p>
            <p className="plan-price">
              {plan.priceKzt === 0 ? "0 ₸" : formatMoney(plan.priceKzt)}
              {plan.priceKzt > 0 ? <small> / мес</small> : null}
            </p>
            <p className="plan-rate">комиссия {rateLabel(plan.rate)} с записи</p>
            <p className="plan-detail">{plan.detail}</p>
            {current === plan.id ? <p className="plan-now">Ваш тариф</p> : null}
          </>
        );
        if (!onPick) {
          return (
            <article key={plan.id} className={className}>
              {inner}
            </article>
          );
        }
        return (
          <button key={plan.id} type="button" className={className} onClick={() => onPick(plan.id)} aria-pressed={current === plan.id}>
            {inner}
          </button>
        );
      })}
    </div>
  );
}

function BookDialog() {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const { bookingSlotId, closeBooking, slots } = useStore();
  const slot = slots.find((item) => item.id === bookingSlotId) ?? null;

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (bookingSlotId && !dialog.open) dialog.showModal();
    if (!bookingSlotId && dialog.open) dialog.close();
  }, [bookingSlotId]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="book-title"
      onClose={closeBooking}
      onClick={(event) => {
        if (event.target === dialogRef.current) closeBooking();
      }}
    >
      {slot ? <BookForm key={slot.id} slot={slot} onClose={closeBooking} /> : null}
    </dialog>
  );
}

function BookForm({ slot, onClose }: { slot: SlotView; onClose: () => void }) {
  const { book, lastClient } = useStore();
  const [name, setName] = useState(lastClient?.name ?? "");
  const [phone, setPhone] = useState(lastClient?.phone ?? "");
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState<string>("");
  const [pending, setPending] = useState(false);
  const end = addMinutes(slot.startsAt, slot.durationMin);

  function submit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    const result = book(slot.id, { name, phone, comment });
    setPending(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    setError("");
    setDone(result.value.id);
  }

  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <p className="kicker">{slot.specialist.service}</p>
          <h2 id="book-title">{done ? "Час ваш" : slot.specialist.name}</h2>
        </div>
        <button type="button" className="icon-btn" onClick={onClose} aria-label="Закрыть">
          Закрыть
        </button>
      </div>
      {done ? (
        <div>
          <p className="code">{done}</p>
          <p>
            {groupLabel(slot.startsAt)}, {formatTime(slot.startsAt)}–{formatTime(end)}. {slot.note}.
          </p>
          <p>Вы платите мастеру {formatMoney(slot.priceKzt)}. Комиссия NEARLY — с мастера, не с вас.</p>
          <p className="muted">Это прототип: заявка не уходит на сервер и видна в кабинете этого браузера.</p>
          <p className="page-actions">
            <Link to="/cabinet" className="btn" onClick={onClose}>В кабинет</Link>
            <button type="button" className="btn btn-ghost" onClick={onClose}>Готово</button>
          </p>
        </div>
      ) : (
        <form className="form" onSubmit={submit}>
          <p>
            {groupLabel(slot.startsAt)}, {formatTime(slot.startsAt)}–{formatTime(end)} · {slot.specialist.district}
          </p>
          <p>{slot.note}</p>
          <p className="price">{formatMoney(slot.priceKzt)} <span className="muted">мастеру</span></p>
          {error ? <p className="error" role="alert">{error}</p> : null}
          <Field label="Как к вам обращаться">
            <input value={name} onChange={(event) => setName(event.target.value)} autoComplete="name" maxLength={80} autoFocus />
          </Field>
          <Field label="Телефон" hint="Мастер увидит его только в кабинете этого браузера.">
            <input value={phone} onChange={(event) => setPhone(event.target.value)} autoComplete="tel" inputMode="tel" placeholder="+7 701 123 45 67" />
          </Field>
          <Field label="Что нужно сделать" hint="Необязательно.">
            <textarea value={comment} onChange={(event) => setComment(event.target.value)} maxLength={300} placeholder="Семейная съёмка, двое детей" />
          </Field>
          <button type="submit" className="btn" disabled={pending}>Забронировать час</button>
        </form>
      )}
    </div>
  );
}
