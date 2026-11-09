import { useEffect } from "react";
import { HashRouter, Link, Route, Routes, useLocation } from "react-router-dom";
import { CabinetPage } from "./pages/Cabinet";
import { HomePage } from "./pages/Home";
import { MasterPage, MastersPage } from "./pages/Masters";
import { PricingPage } from "./pages/Pricing";
import { StoreProvider } from "./store";
import { Shell, useTitle } from "./ui";

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    const query = window.location.hash.split("?")[1] ?? "";
    if (new URLSearchParams(query).get("focus") === "hours") return;
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

function NotFound() {
  useTitle("Страница не найдена — NEARLY");
  return (
    <main className="wrap page">
      <p className="kicker">404</p>
      <h1>Такой страницы нет.</h1>
      <p className="lede">Вернитесь к свободным часам Атырау.</p>
      <p className="page-actions">
        <Link to="/" className="btn">На ленту</Link>
      </p>
    </main>
  );
}

export function App() {
  return (
    <StoreProvider>
      <HashRouter>
        <Shell>
          <ScrollToTop />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/masters" element={<MastersPage />} />
            <Route path="/masters/:id" element={<MasterPage />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/cabinet" element={<CabinetPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Shell>
      </HashRouter>
    </StoreProvider>
  );
}
