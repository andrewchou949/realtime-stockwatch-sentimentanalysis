import { startTransition, useEffect, useState } from "react";

import { api } from "./api.js";

const initialForm = {
  symbol: "",
  thresholdPct: "2.0",
};

const initialDemoForm = {
  symbol: "TSLA",
  direction: "UP",
  pctChange: "6.0",
};

const themeStorageKey = "stock-watch-theme";

function getInitialTheme() {
  const savedTheme = window.localStorage.getItem(themeStorageKey);
  if (savedTheme === "light" || savedTheme === "dark") {
    return savedTheme;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function formatCurrency(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }

  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function formatDate(value) {
  if (!value) {
    return "N/A";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function EmptyState({ title, description }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <span>{description}</span>
    </div>
  );
}

function WatchlistRow({ item, onRemove }) {
  const trendClass =
    item.pct_change_from_baseline === null || item.pct_change_from_baseline === undefined
      ? "trend-flat"
      : item.pct_change_from_baseline >= 0
        ? "trend-up"
        : "trend-down";

  return (
    <article className="watch-card">
      <div className="watch-card__header">
        <div>
          <p className="eyebrow">Ticker</p>
          <h3>{item.symbol}</h3>
        </div>
        <button className="ghost-button" type="button" onClick={() => onRemove(item.symbol)}>
          Remove
        </button>
      </div>

      <div className="metric-row">
        <div>
          <span className="metric-label">Baseline</span>
          <strong>{formatCurrency(item.baseline_price)}</strong>
        </div>
        <div>
          <span className="metric-label">Current</span>
          <strong>{formatCurrency(item.last_price)}</strong>
        </div>
        <div>
          <span className="metric-label">Threshold</span>
          <strong>{item.threshold_pct.toFixed(2)}%</strong>
        </div>
      </div>

      <div className="watch-card__footer">
        <div>
          <span className="metric-label">Baseline At</span>
          <strong>{formatDate(item.baseline_at)}</strong>
        </div>
        <div>
          <span className="metric-label">Last Updated</span>
          <strong>{formatDate(item.last_updated_at)}</strong>
        </div>
        <div>
          <span className="metric-label">From Baseline</span>
          <strong className={trendClass}>{formatPercent(item.pct_change_from_baseline)}</strong>
        </div>
      </div>
    </article>
  );
}

function AlertRow({ alert }) {
  const trendClass = alert.direction === "UP" ? "trend-up" : "trend-down";

  return (
    <article className="alert-row">
      <div>
        <p className="eyebrow">Alert</p>
        <strong>
          {alert.symbol} {alert.direction}
        </strong>
        <span>{formatDate(alert.triggered_at)}</span>
      </div>
      <div className="alert-row__metrics">
        <strong className={trendClass}>{formatPercent(alert.pct_change)}</strong>
        <span>{formatCurrency(alert.current_price)}</span>
      </div>
    </article>
  );
}

function StatCard({ label, value, hint }) {
  return (
    <article className="stat-card">
      <p className="eyebrow">{label}</p>
      <strong>{value}</strong>
      <span>{hint}</span>
    </article>
  );
}

export default function App() {
  const [watchlist, setWatchlist] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [demoForm, setDemoForm] = useState(initialDemoForm);
  const [theme, setTheme] = useState(getInitialTheme);
  const [status, setStatus] = useState("Ready.");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [checkingHealth, setCheckingHealth] = useState(false);
  const [lookupSymbol, setLookupSymbol] = useState("AAPL");
  const [lookupResult, setLookupResult] = useState(null);
  const [lookupError, setLookupError] = useState("");
  const [lookingUp, setLookingUp] = useState(false);
  const [devToolsEnabled, setDevToolsEnabled] = useState(false);
  const [forcingBreach, setForcingBreach] = useState(false);
  const [resettingDemo, setResettingDemo] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem(themeStorageKey, theme);
  }, [theme]);

  async function loadDashboard(message) {
    setLoading(true);
    setError("");

    try {
      const [watchlistItems, recentAlerts, rootPayload] = await Promise.all([
        api.listWatchlist(),
        api.listAlerts(10),
        api.getApiRoot(),
      ]);

      startTransition(() => {
        setWatchlist(watchlistItems);
        setAlerts(recentAlerts);
        setDevToolsEnabled(Boolean(rootPayload.dev_tools_enabled));
        if (message) {
          setStatus(message);
        }
      });
    } catch (loadError) {
      setError(loadError.message);
      setStatus("Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard("Connected to backend.");
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    try {
      await api.addWatchlistItem({
        symbol: form.symbol,
        threshold_pct: Number(form.thresholdPct),
      });
      const addedSymbol = form.symbol.trim().toUpperCase();
      setForm(initialForm);
      setDemoForm((current) => ({ ...current, symbol: addedSymbol || current.symbol }));
      await loadDashboard(`Added ${addedSymbol} to the watchlist.`);
    } catch (submitError) {
      setError(submitError.message);
    }
  }

  async function handleRemove(symbol) {
    setError("");

    try {
      await api.deleteWatchlistItem(symbol);
      await loadDashboard(`Removed ${symbol} from the watchlist.`);
    } catch (removeError) {
      setError(removeError.message);
    }
  }

  async function handleRefresh() {
    setRefreshing(true);
    setError("");

    try {
      const result = await api.refreshWatchlist();
      await loadDashboard(
        `Refreshed ${result.refreshed} symbols. Alerts created: ${result.alerts_created}.`,
      );
    } catch (refreshError) {
      setError(refreshError.message);
    } finally {
      setRefreshing(false);
    }
  }

  async function handleHealthCheck() {
    setCheckingHealth(true);
    setError("");

    try {
      const response = await api.getHealth();
      setStatus(`API healthy. Server timestamp: ${response.timestamp}.`);
    } catch (healthError) {
      setError(healthError.message);
    } finally {
      setCheckingHealth(false);
    }
  }

  async function handlePriceLookup(event) {
    event.preventDefault();
    setLookingUp(true);
    setLookupError("");

    try {
      const result = await api.getPriceSnapshot(lookupSymbol);
      setLookupResult(result);
      setStatus(`Fetched live price for ${result.symbol}.`);
    } catch (lookupFailure) {
      setLookupResult(null);
      setLookupError(lookupFailure.message);
    } finally {
      setLookingUp(false);
    }
  }

  async function handleForceBreach(event) {
    event.preventDefault();
    setForcingBreach(true);
    setError("");

    try {
      const response = await api.forceBreach({
        symbol: demoForm.symbol,
        direction: demoForm.direction,
        pct_change: Number(demoForm.pctChange),
      });
      await loadDashboard(response.message);
    } catch (forceError) {
      setError(forceError.message);
    } finally {
      setForcingBreach(false);
    }
  }

  async function handleResetDemo() {
    setResettingDemo(true);
    setError("");

    try {
      const response = await api.resetDemoState({ scope: "all" });
      setLookupResult(null);
      await loadDashboard(response.message);
    } catch (resetError) {
      setError(resetError.message);
    } finally {
      setResettingDemo(false);
    }
  }

  const symbolCount = watchlist.length;
  const activeAlerts = alerts.length;
  const avgThreshold = symbolCount
    ? `${(watchlist.reduce((sum, item) => sum + item.threshold_pct, 0) / symbolCount).toFixed(1)}%`
    : "N/A";

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div className="hero-panel__topbar">
          <p className="eyebrow">Stock Watch v0.7</p>
          <button
            className="theme-toggle"
            type="button"
            onClick={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
          >
            {theme === "dark" ? "Switch to Light" : "Switch to Dark"}
          </button>
        </div>

        <div className="hero-panel__copy">
          <h1>Baseline alerts with a clean split between frontend and backend.</h1>
          <p className="hero-text">
            This dashboard runs from <code>v0/frontend</code> and talks to the FastAPI API in
            <code> v0/backend</code>.
          </p>
        </div>

        <div className="hero-panel__stats">
          <StatCard label="Watchlist" value={symbolCount} hint="Tracked symbols ready for refresh" />
          <StatCard label="Alerts" value={activeAlerts} hint="Stored threshold events" />
          <StatCard label="Avg Threshold" value={avgThreshold} hint="Across the active watchlist" />
        </div>

        <div className="hero-panel__actions">
          <button className="primary-button" type="button" onClick={handleRefresh} disabled={refreshing}>
            {refreshing ? "Refreshing..." : "Refresh Watchlist"}
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={handleHealthCheck}
            disabled={checkingHealth}
          >
            {checkingHealth ? "Checking..." : "Check API Health"}
          </button>
        </div>

        <div className="status-bar">
          <strong>Status</strong>
          <span>{status}</span>
        </div>
        {error ? <div className="error-banner">{error}</div> : null}
      </section>

      <section className="dashboard-grid">
        <div className="stack">
          <section className="panel panel--warm">
            <div className="panel__header">
              <div>
                <p className="eyebrow">Watchlist Input</p>
                <h2>Add a symbol</h2>
              </div>
              <span className="chip">Baseline captured on create</span>
            </div>

            <form className="form-grid" onSubmit={handleSubmit}>
              <label>
                <span>Symbol</span>
                <input
                  value={form.symbol}
                  onChange={(event) => setForm((current) => ({ ...current, symbol: event.target.value }))}
                  placeholder="AAPL"
                  maxLength={10}
                  required
                />
              </label>

              <label>
                <span>Threshold %</span>
                <input
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={form.thresholdPct}
                  onChange={(event) =>
                    setForm((current) => ({ ...current, thresholdPct: event.target.value }))
                  }
                  required
                />
              </label>

              <button className="primary-button form-submit" type="submit">
                Add To Watchlist
              </button>
            </form>
          </section>

          <section className="panel panel--muted">
            <div className="panel__header">
              <div>
                <p className="eyebrow">Prices</p>
                <h2>Quick price lookup</h2>
              </div>
            </div>

            <form className="lookup-form" onSubmit={handlePriceLookup}>
              <input
                value={lookupSymbol}
                onChange={(event) => setLookupSymbol(event.target.value)}
                placeholder="TSLA"
                maxLength={10}
              />
              <button className="secondary-button" type="submit" disabled={lookingUp}>
                {lookingUp ? "Fetching..." : "Fetch Price"}
              </button>
            </form>

            {lookupError ? <div className="error-inline">{lookupError}</div> : null}
            {lookupResult ? (
              <div className="lookup-result">
                <strong>{lookupResult.symbol}</strong>
                <span>{formatCurrency(lookupResult.price)}</span>
                <span>{formatDate(lookupResult.timestamp)}</span>
              </div>
            ) : (
              <EmptyState
                title="Lookup any symbol"
                description="Use the backend price endpoint directly from the frontend."
              />
            )}
          </section>

          {devToolsEnabled ? (
            <section className="panel panel--demo">
              <div className="panel__header">
                <div>
                  <p className="eyebrow">Demo Tools</p>
                  <h2>Stage a clean walkthrough</h2>
                </div>
                <span className="chip">Dev only</span>
              </div>

              <form className="demo-form" onSubmit={handleForceBreach}>
                <label>
                  <span>Symbol</span>
                  <input
                    value={demoForm.symbol}
                    onChange={(event) =>
                      setDemoForm((current) => ({ ...current, symbol: event.target.value }))
                    }
                    placeholder="TSLA"
                    maxLength={10}
                    required
                  />
                </label>

                <label>
                  <span>Direction</span>
                  <select
                    value={demoForm.direction}
                    onChange={(event) =>
                      setDemoForm((current) => ({ ...current, direction: event.target.value }))
                    }
                  >
                    <option value="UP">UP</option>
                    <option value="DOWN">DOWN</option>
                  </select>
                </label>

                <label>
                  <span>Percent Move</span>
                  <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={demoForm.pctChange}
                    onChange={(event) =>
                      setDemoForm((current) => ({ ...current, pctChange: event.target.value }))
                    }
                    required
                  />
                </label>

                <div className="demo-actions">
                  <button className="secondary-button" type="submit" disabled={forcingBreach}>
                    {forcingBreach ? "Forcing..." : "Force Breach"}
                  </button>
                  <button
                    className="ghost-button ghost-button--soft"
                    type="button"
                    onClick={handleResetDemo}
                    disabled={resettingDemo}
                  >
                    {resettingDemo ? "Resetting..." : "Reset Demo State"}
                  </button>
                </div>
              </form>
            </section>
          ) : null}
        </div>

        <section className="panel panel--dark">
          <div className="panel__header">
            <div>
              <p className="eyebrow">Live Watchlist View</p>
              <h2>Tracked symbols</h2>
            </div>
            <span className="chip chip--dark">{watchlist.length} symbols</span>
          </div>

          <div className="watchlist-stack">
            {loading ? (
              <EmptyState title="Loading watchlist" description="Pulling symbols from the backend." />
            ) : watchlist.length ? (
              watchlist.map((item) => (
                <WatchlistRow key={item.symbol} item={item} onRemove={handleRemove} />
              ))
            ) : (
              <EmptyState
                title="No symbols yet"
                description="Add your first ticker to capture a baseline and start tracking movement."
              />
            )}
          </div>
        </section>
      </section>

      <section className="panel panel--alerts">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Alert History</p>
            <h2>Recent threshold events</h2>
          </div>
          <span className="chip">Latest 10</span>
        </div>

        <div className="alerts-grid">
          {loading ? (
            <EmptyState title="Loading alerts" description="Checking for recent threshold breaches." />
          ) : alerts.length ? (
            alerts.map((alert) => <AlertRow key={`${alert.id}-${alert.triggered_at}`} alert={alert} />)
          ) : (
            <EmptyState
              title="No alerts yet"
              description="Refresh the watchlist after the market moves to see stored alerts appear here."
            />
          )}
        </div>
      </section>
    </main>
  );
}
