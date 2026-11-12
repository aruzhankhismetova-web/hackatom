import { useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  CATEGORIES,
  DISTRICTS,
  PROMPTS,
  addMinutes,
  asWhen,
  byTime,
  commissionOf,
  countLabel,
  filterSlots,
  formatMoney,
  formatTime,
  groupLabel,
  inferWhen,
  planById,
  rateLabel,
  specialistReceives,
  type SlotView,
  type WhenFilter,
} from "../model";
import { useStore } from "../store";
import { PlanCards, SlotRow, useTitle } from "../ui";

const WHENS: { id: WhenFilter; label: string }[] = [
  { id: "any", label: "Все дни" },
  { id: "today", label: "Сегодня" },
  { id: "tomorrow", label: "Завтра" },
  { id: "week", label: "Неделя" },
];

export function HomePage() {
  useTitle("NEARLY — найди специалиста рядом в Атырау");
  const { openSlots, specialists, now, openBooking } = useStore();
  const [params, setParams] = useSearchParams();
  const q = params.get("q") ?? "";
  const when = asWhen(params.get("when"));
  const category = params.get("category") ?? "all";
  const district = params.get("district") ?? "all";
  const effectiveWhen = inferWhen(q, when);
  const visible = filterSlots(openSlots, { q, when, category, district }, now);
  const allInView = filterSlots(openSlots, { q, when, category: "all", district }, now);
  const groups = groupVisible(visible, now);
  const soon = [...openSlots].sort(byTime).slice(0, 3);
  const next = soon[0];

  function update(patch: Record<string, string | null>) {
    const nextParams = new URLSearchParams(params);
    for (const [key, value] of Object.entries(patch)) {
      if (!value || value === "all" || value === "any") nextParams.delete(key);
      else nextParams.set(key, value);
    }
    nextParams.delete("focus");
    setParams(nextParams, { replace: true });
  }

  useEffect(() => {
    if (params.get("focus") !== "hours") return;
    document.getElementById("hours")?.scrollIntoView({ behavior: "smooth", block: "start" });
    const nextParams = new URLSearchParams(params);
    nextParams.delete("focus");
    setParams(nextParams, { replace: true });
  }, [params, setParams]);

  function pickWhen(id: WhenFilter) {
    if (effectiveWhen === id && id !== "any") {
      const cleaned = q.replace(/на завтра|на сегодня|на этой неделе|на неделе|завтра|сегодня/gi, " ").replace(/\s+/g, " ").trim();
      update({ when: null, q: cleaned || null });
      return;
    }
    update({ when: id === "any" ? null : id });
  }

  return (
    <main>
      <section className="wrap hero">
        <div>
          <p className="kicker">Атырау · маркетплейс начинающих</p>
          <h1>Найди специалиста <em>рядом</em>.</h1>
          <p className="lede">
            Фотограф на завтра, мастер маникюра, репетитор, дизайнер или видеограф на мероприятие.
            Специалисты открывают свободные часы — вы бронируете конкретное время, а не оставляете заявку в пустоту.
          </p>
          <form
            className="search"
            role="search"
            onSubmit={(event) => {
              event.preventDefault();
              document.getElementById("hours")?.scrollIntoView({ behavior: "smooth", block: "start" });
            }}
          >
            <input
              value={q}
              onChange={(event) => update({ q: event.target.value })}
              placeholder="Кого ищете?"
              aria-label="Кого ищете"
            />
            <div className="when" aria-label="Когда">
              {WHENS.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={effectiveWhen === item.id ? "chip on" : "chip"}
                  aria-pressed={effectiveWhen === item.id}
                  onClick={() => pickWhen(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </div>
            <button type="submit" className="btn">Найти</button>
          </form>
          <div className="prompts">
            {PROMPTS.map((prompt) => (
              <button
                key={prompt.label}
                type="button"
                className="prompt"
                onClick={() => {
                  update({ q: prompt.q, when: prompt.when, category: null, district: null });
                  document.getElementById("hours")?.scrollIntoView({ behavior: "smooth", block: "start" });
                }}
              >
                {prompt.label}
              </button>
            ))}
          </div>
          <p className="stats">
            <span><strong>{countLabel(openSlots.length, ["открытый час", "открытых часа", "открытых часов"])}</strong></span>
            <span><strong>{countLabel(specialists.length, ["специалист", "специалиста", "специалистов"])}</strong></span>
            <span><strong>один город</strong></span>
          </p>
        </div>
        <aside className="sheet" aria-label="Ближайшие часы">
          <h2>Ближайшие часы</h2>
          {soon.map((slot) => (
            <div className="sheet-row" key={slot.id}>
              <div>
                <p className="sheet-when">{groupLabel(slot.startsAt, now)} · {formatTime(slot.startsAt)}</p>
                <p className="sheet-name">
                  <Link to={`/masters/${slot.specialist.id}`}>{slot.specialist.name}</Link>
                </p>
                <p className="muted">{slot.specialist.service} · {slot.specialist.district}</p>
              </div>
              <div className="sheet-side">
                <p className="price">{formatMoney(slot.priceKzt)}</p>
                <button type="button" className="btn btn-small" onClick={() => openBooking(slot.id)}>Занять</button>
              </div>
            </div>
          ))}
          <p className="sheet-foot">
            <a href="#hours" onClick={(event) => {
              event.preventDefault();
              document.getElementById("hours")?.scrollIntoView({ behavior: "smooth", block: "start" });
            }}>Вся лента</a>
          </p>
        </aside>
      </section>

      <section className="wrap section" id="hours">
        <div className="banner">
          Анкеты на ленте учебные — так виден живой Атырау. Новая запись и новый час сохраняются только в этом браузере.
        </div>
        <div className="section-head">
          <h2>Свободные часы</h2>
          <p className="lede">Мастер публикует время, когда он действительно свободен. Бронь садится на этот час.</p>
        </div>
        <div className="filters" aria-label="Услуги">
          <button type="button" className={category === "all" ? "chip on" : "chip"} onClick={() => update({ category: null })}>
            Все <span className="count">{allInView.length}</span>
          </button>
          {CATEGORIES.map((item) => {
            const count = filterSlots(openSlots, { q, when, category: item.id, district }, now).length;
            return (
              <button
                key={item.id}
                type="button"
                className={category === item.id ? "chip on" : "chip"}
                aria-pressed={category === item.id}
                onClick={() => update({ category: category === item.id ? null : item.id })}
              >
                {item.label} <span className="count">{count}</span>
              </button>
            );
          })}
        </div>
        <div className="filters" aria-label="Районы">
          <button type="button" className={district === "all" ? "chip on" : "chip"} onClick={() => update({ district: null })}>
            Все районы
          </button>
          {DISTRICTS.map((item) => (
            <button
              key={item}
              type="button"
              className={district === item ? "chip on" : "chip"}
              aria-pressed={district === item}
              onClick={() => update({ district: district === item ? null : item })}
            >
              {item}
            </button>
          ))}
        </div>
        <p className="result-line" aria-live="polite">
          {countLabel(visible.length, ["открытый час", "открытых часа", "открытых часов"])}
          {category !== "all" ? ` · ${CATEGORIES.find((item) => item.id === category)?.label}` : ""}
          {district !== "all" ? ` · ${district}` : ""}
          {effectiveWhen !== "any" ? ` · ${WHENS.find((item) => item.id === effectiveWhen)?.label.toLowerCase()}` : ""}
        </p>
        {groups.length === 0 ? (
          <div className="empty">
            <p>На это время часов нет. Снимите фильтр или откройте свой час — в Атырау как раз нужна плотность ленты.</p>
            <p className="page-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setParams({}, { replace: true })}>Сбросить фильтры</button>
              <Link to="/cabinet" className="btn">Открыть час</Link>
            </p>
          </div>
        ) : (
          groups.map((group) => (
            <section key={group.key} aria-label={group.label}>
              <h3 className="day-head">{group.label}</h3>
              {group.slots.map((slot) => (
                <SlotRow key={slot.id} slot={slot} />
              ))}
            </section>
          ))
        )}
      </section>

      <section className="wrap section split">
        <div>
          <h2>Это не каталог организаций.</h2>
          <p className="lede">
            В каталоге — вывески и кнопка «оставьте заявку». Здесь люди, которые только набирают практику и готовы взять заказ в конкретный час.
          </p>
          <ol className="steps">
            <li>
              <span>01</span>
              <h3>Мастер открывает час</h3>
              <p>Не абонемент и не объявление на месяц. Время, когда он свободен.</p>
            </li>
            <li>
              <span>02</span>
              <h3>Вы его забираете</h3>
              <p>Фото, маникюр, урок, макет или съёмка мероприятия — бронь на этот слот.</p>
            </li>
            <li>
              <span>03</span>
              <h3>Встречаетесь в Атырау</h3>
              <p>Клиент платит мастеру. NEARLY берёт комиссию только с записи.</p>
            </li>
          </ol>
          <blockquote className="pull">Каталог продаёт вывески. NEARLY продаёт свободный час живого человека.</blockquote>
        </div>
        {next ? <Receipt slot={next} /> : null}
      </section>

      <section className="wrap section">
        <div className="section-head">
          <h2>Деньги с записи, не с надежды.</h2>
          <p className="lede">Начинающему мастеру не нужно платить за рекламу, пока нет клиентов. Подписка уменьшает комиссию и поднимает час внутри дня.</p>
        </div>
        <PlanCards />
        <p className="page-actions">
          <Link to="/pricing" className="btn">Как считается комиссия</Link>
          <Link to="/cabinet" className="btn btn-ghost">Я специалист</Link>
        </p>
      </section>
    </main>
  );
}

function groupVisible(slots: SlotView[], now: Date) {
  const groups: { key: string; label: string; slots: SlotView[] }[] = [];
  for (const slot of slots) {
    const label = groupLabel(slot.startsAt, now);
    const key = label;
    const last = groups[groups.length - 1];
    if (!last || last.key !== key) groups.push({ key, label, slots: [slot] });
    else last.slots.push(slot);
  }
  return groups;
}

function Receipt({ slot }: { slot: SlotView }) {
  const plan = planById(slot.specialist.plan);
  const commission = commissionOf(slot.priceKzt, plan.id);
  return (
    <aside className="receipt" aria-label="Пример расчёта">
      <p className="kicker">Как проходят деньги</p>
      <p className="receipt-title">{slot.specialist.name}</p>
      <p>{groupLabel(slot.startsAt)} · {formatTime(slot.startsAt)}–{formatTime(addMinutes(slot.startsAt, slot.durationMin))}</p>
      <p>{slot.note}</p>
      <dl>
        <div>
          <dt>Клиент платит мастеру</dt>
          <dd>{formatMoney(slot.priceKzt)}</dd>
        </div>
        <div>
          <dt>Комиссия NEARLY, тариф «{plan.name}», {rateLabel(plan.rate)}</dt>
          <dd>{formatMoney(commission)}</dd>
        </div>
        <div>
          <dt>Мастеру остаётся</dt>
          <dd>{formatMoney(specialistReceives(slot.priceKzt, slot.specialist.plan))}</dd>
        </div>
      </dl>
    </aside>
  );
}
