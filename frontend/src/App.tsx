import { useEffect, useState, useCallback, useMemo } from "react";
import "./styles/index.css";

interface Departure {
  time: string;
  minutes_away: number;
  delay_seconds: number | null;
  destination: string | null;
}

interface LineData {
  line_name: string;
  stop_name: string;
  departures: Departure[];
}

interface Commute {
  id: string;
  label: string;
  lines: LineData[];
}

interface ApiResponse {
  commutes: Commute[];
  schedule_type: string;
  date: string;
  day_of_week: string;
}

interface MergedDeparture extends Departure {
  line_name: string;
}

const REFRESH_INTERVAL = 30_000; // 30s to keep RT data fresh

function formatDelay(seconds: number | null): { text: string; className: string } {
  if (seconds === null) return { text: "", className: "" };
  if (seconds >= -30 && seconds <= 60) return { text: "on time", className: "delay-ok" };
  if (seconds > 60) {
    const min = Math.round(seconds / 60);
    return { text: `+${min} min`, className: "delay-late" };
  }
  const min = Math.round(Math.abs(seconds) / 60);
  return { text: `-${min} min`, className: "delay-early" };
}

function formatMinutes(min: number): string {
  if (min < 1) return "now";
  if (min < 60) return `${min} min`;
  const h = Math.floor(min / 60);
  const m = min % 60;
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

function App() {
  const [commutes, setCommutes] = useState<Commute[]>([]);
  const [scheduleInfo, setScheduleInfo] = useState<{ type: string; date: string; day: string } | null>(null);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch("/api/mpk/departures");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: ApiResponse = await res.json();
      setCommutes(data.commutes);
      setScheduleInfo({ type: data.schedule_type, date: data.date, day: data.day_of_week });
      setError(null);
      setLastUpdated(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchData]);

  const active = commutes.find((c) => c.id === activeId) ?? null;

  const merged = useMemo<MergedDeparture[]>(() => {
    if (!active) return [];
    const all: MergedDeparture[] = [];
    for (const line of active.lines) {
      for (const dep of line.departures) {
        all.push({ ...dep, line_name: line.line_name });
      }
    }
    all.sort((a, b) => a.minutes_away - b.minutes_away);
    return all;
  }, [active]);

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading departures...</div>
      </div>
    );
  }

  // Direction picker
  if (!active) {
    return (
      <div className="container">
        <header className="header">
          <h1>New Salt City Bus</h1>
          <p className="subtitle">53A &middot; 53B</p>
        </header>
        {error && <div className="error-banner">{error}</div>}
        <div className="picker">
          {commutes.map((c) => (
            <button key={c.id} className="picker-btn" onClick={() => setActiveId(c.id)}>
              {c.label}
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Departure list
  return (
    <div className="container">
      <header className="header">
        <button className="back-btn" onClick={() => setActiveId(null)}>&larr;</button>
        <div>
          <h1>{active.label}</h1>
          <p className="subtitle">{active.lines.map((l) => l.stop_name).join(" / ")}</p>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {merged.length === 0 ? (
        <p className="no-departures">No more departures today</p>
      ) : (
        <ul className="departure-list">
          {merged.map((dep, i) => (
            <li key={i} className={`departure-item ${i === 0 ? "next" : ""}`}>
              <div className="dep-left">
                <span className="line-badge small">{dep.line_name}</span>
                <span className="dep-time">{dep.time}</span>
                {(() => {
                  const d = formatDelay(dep.delay_seconds);
                  return d.text ? <span className={`delay-tag ${d.className}`}>{d.text}</span> : null;
                })()}
              </div>
              <div className="dep-right">
                {dep.destination && <span className="dep-dest">{dep.destination}</span>}
                <span className="dep-away">{formatMinutes(dep.minutes_away)}</span>
              </div>
            </li>
          ))}
        </ul>
      )}

      {lastUpdated && (
        <footer className="footer">
          <div className="footer-top">
            {scheduleInfo && (
              <span className="schedule-info">
                {scheduleInfo.date} ({scheduleInfo.day}) &middot; {scheduleInfo.type}
              </span>
            )}
          </div>
          <div className="footer-bottom">
            <span>Updated {lastUpdated.toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" })}</span>
            <button className="refresh-btn" onClick={fetchData}>Refresh</button>
          </div>
        </footer>
      )}
    </div>
  );
}

export default App;
