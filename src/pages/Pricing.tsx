import { useState } from "react";
import { Link } from "react-router-dom";
import { PLANS, commissionOf, formatMoney, planById, rateLabel, specialistReceives, type PlanId } from "../model";
import { PlanCards, useTitle } from "../ui";

const EXAMPLES = [7000, 12000, 35000];

export function PricingPage() {
  useTitle("Комиссия и подписка — NEARLY");
  const [raw, setRaw] = useState("12000");
  const [planId, setPlanId] = useState<PlanId>("practice");
  const digits = raw.replace(/\s/g, "");
  const price = /^\d+$/.test(digits) ? Number(digits) : null;
  const valid = price !== null && price >= 1000 && price <= 500000;
  const plan = planById(planId);

  return (
    <main className="wrap page">
      <p className="kicker">Монетизация</p>
      <h1>Комиссия с брони и подписка мастера.</h1>
      <p className="lede">
        NEARLY зарабатывает дважды, и оба раза с той стороны, где появляются деньги.
        Клиент платит мастеру цену из ленты. Комиссия удерживается с мастера после записи.
        Подписка — если мастер хочет отдавать меньше с каждого часа и стоять выше внутри своего дня.
      </p>
      <PlanCards current={planId} onPick={setPlanId} />
      <p className="muted plan-note">Нажмите тариф, чтобы пересчитать пример. В прототипе оплата не списывается — в кабинете тариф меняет ленту по-настоящему.</p>

      <section className="section calc">
        <div>
          <h2>Пример на одной записи</h2>
          <label className="field">
            <span>Цена для клиента, ₸</span>
            <input value={raw} onChange={(event) => setRaw(event.target.value)} inputMode="numeric" />
          </label>
          <div className="filters">
            {EXAMPLES.map((amount) => (
              <button key={amount} type="button" className={digits === String(amount) ? "chip on" : "chip"} onClick={() => setRaw(String(amount))}>
                {formatMoney(amount)}
              </button>
            ))}
          </div>
          <ul className="plain">
            {PLANS.map((item) => (
              <li key={item.id}>
                «{item.name}»: {item.priceKzt === 0 ? "без абонентской платы" : `${formatMoney(item.priceKzt)} в месяц`}, комиссия {rateLabel(item.rate)}, до {item.openSlotLimit} открытых часов.
              </li>
            ))}
          </ul>
        </div>
        <div className="calc-result">
          {valid && price !== null ? (
            <>
              <p className="kicker">Тариф «{plan.name}»</p>
              <dl>
                <div>
                  <dt>Клиент платит мастеру</dt>
                  <dd>{formatMoney(price)}</dd>
                </div>
                <div>
                  <dt>NEARLY забирает {rateLabel(plan.rate)}</dt>
                  <dd>{formatMoney(commissionOf(price, plan.id))}</dd>
                </div>
                <div>
                  <dt>Мастеру остаётся</dt>
                  <dd>{formatMoney(specialistReceives(price, plan.id))}</dd>
                </div>
                <div>
                  <dt>Подписка отдельно</dt>
                  <dd>{plan.priceKzt === 0 ? "0 ₸" : `${formatMoney(plan.priceKzt)} / мес`}</dd>
                </div>
              </dl>
            </>
          ) : (
            <p>Введите цену от 1 000 до 500 000 ₸.</p>
          )}
        </div>
      </section>

      <section className="section">
        <h2>Почему так, а не реклама</h2>
        <p className="lede">
          Объявление на месяц продаёт надежду. Начинающий мастер в Атырау часто не может заплатить за него до первой записи.
          Комиссия появляется только когда час заняли. Подписка имеет смысл, когда заказы уже идут каждую неделю: комиссия падает, а час «Рядом» встаёт выше других часов того же дня. Часы другого дня он не перепрыгивает — сегодняшняя свобода важнее тарифа.
        </p>
        <p className="page-actions">
          <Link to="/cabinet" className="btn">Открыть анкету</Link>
          <Link to="/?focus=hours" className="btn btn-ghost">Смотреть ленту</Link>
        </p>
      </section>
    </main>
  );
}
