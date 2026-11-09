import { Link, useParams, useSearchParams } from "react-router-dom";
import {
  CATEGORIES,
  DISTRICTS,
  byTime,
  formatMoney,
  formatTime,
  groupLabel,
  matchesSpecialist,
  planById,
} from "../model";
import { useStore } from "../store";
import { Monogram, SlotRow, useTitle } from "../ui";

export function MastersPage() {
  useTitle("Специалисты Атырау — NEARLY");
  const { specialists, openSlots } = useStore();
  const [params, setParams] = useSearchParams();
  const q = params.get("q") ?? "";
  const category = params.get("category") ?? "all";
  const district = params.get("district") ?? "all";

  function update(patch: Record<string, string | null>) {
    const next = new URLSearchParams(params);
    for (const [key, value] of Object.entries(patch)) {
      if (!value || value === "all") next.delete(key);
      else next.set(key, value);
    }
    setParams(next, { replace: true });
  }

  const people = specialists
    .map((specialist) => ({
      specialist,
      next: openSlots.filter((slot) => slot.specialistId === specialist.id).sort(byTime)[0] ?? null,
    }))
    .filter(({ specialist, next }) => {
      if (category !== "all" && specialist.category !== category) return false;
      if (district !== "all" && specialist.district !== district) return false;
      const extra = next ? `${next.note} ${formatTime(next.startsAt)}` : "";
      return matchesSpecialist(specialist, extra, q);
    })
    .sort((a, b) => {
      if (a.next && b.next) return byTime(a.next, b.next);
      if (a.next) return -1;
      if (b.next) return 1;
      return a.specialist.name.localeCompare(b.specialist.name, "ru");
    });

  return (
    <main className="wrap page">
      <p className="kicker">Люди, не организации</p>
      <h1>Специалисты Атырау</h1>
      <p className="lede">Начинающие мастера. Рядом с именем — ближайший свободный час, если он есть.</p>
      <form className="search" role="search" onSubmit={(event) => event.preventDefault()}>
        <input value={q} onChange={(event) => update({ q: event.target.value })} placeholder="Имя или услуга" aria-label="Имя или услуга" />
      </form>
      <div className="filters">
        <button type="button" className={category === "all" ? "chip on" : "chip"} onClick={() => update({ category: null })}>Все</button>
        {CATEGORIES.map((item) => (
          <button key={item.id} type="button" className={category === item.id ? "chip on" : "chip"} onClick={() => update({ category: category === item.id ? null : item.id })}>
            {item.label}
          </button>
        ))}
      </div>
      <div className="filters">
        <button type="button" className={district === "all" ? "chip on" : "chip"} onClick={() => update({ district: null })}>Все районы</button>
        {DISTRICTS.map((item) => (
          <button key={item} type="button" className={district === item ? "chip on" : "chip"} onClick={() => update({ district: district === item ? null : item })}>
            {item}
          </button>
        ))}
      </div>
      {people.length === 0 ? (
        <div className="empty">
          <p>Никого не нашли. Сбросьте фильтр или откройте анкету — в этой услуге как раз мало людей.</p>
          <p className="page-actions">
            <button type="button" className="btn btn-ghost" onClick={() => setParams({}, { replace: true })}>Сбросить</button>
            <Link to="/cabinet" className="btn">Открыть анкету</Link>
          </p>
        </div>
      ) : (
        <div className="people">
          {people.map(({ specialist, next }) => (
            <Link key={specialist.id} to={`/masters/${specialist.id}`} className="person">
              <Monogram name={specialist.name} tone={specialist.tone} />
              <span>
                <h2>{specialist.name}</h2>
                <p>{specialist.service} · {specialist.district}</p>
                <p className="muted">{specialist.bio}</p>
              </span>
              <span className="person-side">
                {next ? (
                  <>
                    <p className="sheet-when">{groupLabel(next.startsAt)} · {formatTime(next.startsAt)}</p>
                    <p className="price">{formatMoney(next.priceKzt)}</p>
                  </>
                ) : (
                  <p className="muted">Нет открытых часов</p>
                )}
              </span>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}

export function MasterPage() {
  const { id } = useParams();
  const { specialists, openSlots } = useStore();
  const specialist = specialists.find((item) => item.id === id);
  useTitle(specialist ? `${specialist.name} · ${specialist.service} — NEARLY` : "Анкета — NEARLY");
  if (!specialist) {
    return (
      <main className="wrap page">
        <h1>Такой анкеты нет.</h1>
        <p className="page-actions"><Link to="/masters" className="btn">Ко всем специалистам</Link></p>
      </main>
    );
  }
  const slots = openSlots.filter((slot) => slot.specialistId === specialist.id).sort(byTime);
  return (
    <main className="wrap page">
      <p className="kicker"><Link to="/masters">Все специалисты</Link></p>
      <div className="profile">
        <Monogram name={specialist.name} tone={specialist.tone} size="lg" />
        <div>
          <h1>{specialist.name}</h1>
          <p className="lede">{specialist.service} · {specialist.district} · от {formatMoney(specialist.priceFromKzt)}</p>
          <p className="meta-line">
            Начинающий · практика {specialist.practice} · тариф «{planById(specialist.plan).name}»
            {specialist.seed ? " · учебная анкета" : " · ваша анкета в этом браузере"}
          </p>
        </div>
      </div>
      <p className="bio">{specialist.bio}</p>
      <h2>Свободные часы</h2>
      {slots.length === 0 ? (
        <div className="empty">
          <p>Сейчас открытых часов нет. Посмотрите ленту — там есть другие мастера на сегодня и завтра.</p>
          <p className="page-actions"><Link to="/?focus=hours" className="btn">К свободным часам</Link></p>
        </div>
      ) : (
        slots.map((slot) => <SlotRow key={slot.id} slot={slot} />)
      )}
    </main>
  );
}
