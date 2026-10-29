import { FormEvent, useEffect, useState } from "react";
import { Activity, ArrowUpRight, Command, Cpu, Mic, ShieldCheck, Sparkles, Terminal, Puzzle, RefreshCw, LockKeyhole, Files, Globe, CalendarDays, MessageSquare } from "lucide-react";

type Result = { source: string; message: string; proposal?: { action_id: string; arguments: Record<string, unknown>; description: string } | null };
type Adapter = { adapter_id: string; display_name: string; description: string; enabled: boolean; health: string; capabilities: { capability_id: string; description: string; data_class: string; requires_confirmation: boolean }[] };

const API = "http://127.0.0.1:8765";
type View = "assistant" | "integrations" | "activity";

const plannedAdapters = [
  { name: "Windows & files", icon: Files, detail: "Open approved apps, search files, and manage local workflows.", phase: "PLANNED" },
  { name: "Browser", icon: Globe, detail: "Use documented browser controls and supported extensions.", phase: "PLANNED" },
  { name: "Productivity", icon: CalendarDays, detail: "Calendar, reminders, and task tools through supported APIs.", phase: "PLANNED" },
  { name: "Messaging", icon: MessageSquare, detail: "Draft first; sending must require an explicit approval step.", phase: "PLANNED" },
];

export default function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [online, setOnline] = useState(false);
  const [busy, setBusy] = useState(false);
  const [view, setView] = useState<View>("assistant");
  const [adapters, setAdapters] = useState<Adapter[]>([]);
  const [checking, setChecking] = useState(false);

  async function refreshCore(): Promise<boolean> {
    setChecking(true);
    try {
      const [healthResponse, integrationResponse] = await Promise.all([
        fetch(API + "/health"),
        fetch(API + "/api/integrations"),
      ]);
      if (!healthResponse.ok || !integrationResponse.ok) throw new Error("Local API unavailable");
      setOnline(true);
      setAdapters(await integrationResponse.json());
      return true;
    } catch {
      setOnline(false);
      setAdapters([]);
      return false;
    } finally {
      setChecking(false);
    }
  }

  useEffect(() => {
    let cancelled = false;
    let timeout: ReturnType<typeof setTimeout>;
    let attempts = 0;
    const poll = async () => {
      const connected = await refreshCore();
      attempts += 1;
      if (!cancelled && !connected && attempts < 12) timeout = setTimeout(poll, 1000);
    };
    void poll();
    return () => { cancelled = true; clearTimeout(timeout); };
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!input.trim() || busy) return;
    setBusy(true);
    try {
      const response = await fetch(API + "/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });
      if (!response.ok) throw new Error("Backend returned " + response.status);
      setResult(await response.json());
      setOnline(true);
    } catch {
      setResult({ source: "offline", message: "Can't reach the local RITS core. Check that port 8765 is free, then restart RITS. The desktop shell normally starts the backend automatically." });
      setOnline(false);
    } finally {
      setBusy(false);
    }
  }

  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand-mark">R<span>.</span></div>
      <div className="brand-copy"><strong>RITS</strong><small>DESKTOP INTELLIGENCE</small></div>
      <div className="sidebar-divider" />
      <div className="nav-label">WORKSPACE</div>
      <button className={`nav-item ${view === "assistant" ? "active" : ""}`} onClick={() => setView("assistant")}><Command size={17} /> Assistant {view === "assistant" && <span className="nav-dot" />}</button>
      <button className={`nav-item ${view === "activity" ? "active" : ""}`} onClick={() => setView("activity")}><Activity size={17} /> Activity {view === "activity" && <span className="nav-dot" />}</button>
      <button className={`nav-item ${view === "integrations" ? "active" : ""}`} onClick={() => setView("integrations")}><Puzzle size={17} /> Integrations {view === "integrations" && <span className="nav-dot" />}</button>
      <div className="sidebar-bottom"><ShieldCheck size={16} /><span>Local-first by design</span></div>
    </aside>
    <section className="main-panel">
      <header className="topbar"><div className="breadcrumb">Workspace <span>/</span> <b>{view[0].toUpperCase() + view.slice(1)}</b></div><div className="connection"><i className={online ? "online" : ""} />{online ? "LOCAL CORE CONNECTED" : "CORE OFFLINE"}</div></header>
      <div className="content">
        {view === "assistant" && <>
          <div className="eyebrow"><span /> PERSONAL DESKTOP ASSISTANT</div>
          <h1>Your day,<br /><span>under control.</span></h1>
          <p className="intro">One calm place to think, automate, and work across your apps.<br />Your local rules work without an AI provider.</p>
          <div className="status-grid">
            <div className="status-card"><div className="card-icon"><Terminal size={18} /></div><div><small>LOCAL AUTOMATION</small><strong>Foundation ready</strong></div><span className="tiny-status">RULES</span></div>
            <div className="status-card"><div className="card-icon purple"><Sparkles size={18} /></div><div><small>AI PROVIDER</small><strong>Not connected</strong></div><span className="tiny-status pending">NEXT</span></div>
            <div className="status-card"><div className="card-icon red"><Mic size={18} /></div><div><small>VOICE / WAKE WORD</small><strong>Not connected</strong></div><span className="tiny-status pending">NEXT</span></div>
          </div>
          <section className="command-panel">
            <div className="panel-heading"><div><span className="live-dot" /> COMMAND CONSOLE</div><span>LOCAL RULES FIRST</span></div>
            <form onSubmit={submit}>
              <textarea value={input} onChange={e => setInput(e.target.value)} placeholder="Try “help”, “status”, or “draft I’ll be there in 10 minutes”" rows={3} />
              <div className="form-footer"><span><ShieldCheck size={14} /> No command is sent to the cloud in this build.</span><button disabled={!input.trim() || busy}>{busy ? "Working…" : "Run command"} <ArrowUpRight size={16} /></button></div>
            </form>
            {result && <div className="result-box"><div className="result-label">{result.source.replace("-", " ").toUpperCase()}</div><p>{result.message}</p>{result.proposal && <div className="proposal"><b>{result.proposal.action_id}</b><span>{result.proposal.description}</span><pre>{JSON.stringify(result.proposal.arguments, null, 2)}</pre></div>}</div>}
          </section>
          <div className="bottom-note"><ShieldCheck size={16} /><span><b>Permission before action.</b> RITS will use registered, limited actions—not unrestricted shell access.</span></div>
        </>}
        {view === "integrations" && <>
          <div className="eyebrow"><span /> CONNECTED WORKSPACE</div>
          <h1>One assistant.<br /><span>Many apps.</span></h1>
          <p className="intro">RITS is designed to work across your desktop. Every integration will declare its capabilities and permissions before it can act.</p>
          <div className="integration-toolbar"><div><Puzzle size={17} /><b>Integration registry</b><span>{adapters.length} enabled</span></div><button className="refresh-button" onClick={() => void refreshCore()} disabled={checking}><RefreshCw size={14} className={checking ? "spin" : ""} /> Refresh</button></div>
          {!online && <div className="notice"><LockKeyhole size={17} /><span>The local core is offline. Start it to load registered integrations.</span></div>}
          {online && adapters.length === 0 && <div className="empty-state"><div className="empty-icon"><Puzzle size={25} /></div><h2>No integrations enabled yet</h2><p>This is intentional. RITS won't claim to control an app until an adapter is implemented, tested, and permissioned.</p></div>}
          {adapters.map(adapter => <div className="registered-adapter" key={adapter.adapter_id}><div className="registered-icon"><Puzzle size={18} /></div><div className="registered-copy"><b>{adapter.display_name}</b><span>{adapter.description}</span><small>{adapter.capabilities.length} capabilities · {adapter.health}</small></div><span className="enabled-pill">ENABLED</span></div>)}
          <div className="section-label">PLANNED ADAPTERS</div>
          <div className="planned-grid">{plannedAdapters.map(item => <div className="planned-card" key={item.name}><div className="planned-top"><item.icon size={18} /><span>{item.phase}</span></div><b>{item.name}</b><p>{item.detail}</p></div>)}</div>
          <div className="bottom-note"><ShieldCheck size={16} /><span><b>Safe by default.</b> Sending messages, modifying files, or changing external state will require explicit approval.</span></div>
        </>}
        {view === "activity" && <>
          <div className="eyebrow"><span /> LOCAL HISTORY</div>
          <h1>Know what<br /><span>RITS did.</span></h1>
          <p className="intro">An inspectable history of commands and actions is planned. This foundation doesn't yet store a persistent activity log.</p>
          <div className="empty-state"><div className="empty-icon"><Activity size={25} /></div><h2>No saved activity yet</h2><p>Persistent, privacy-conscious local history will be added after the core command and permission flows are established.</p></div>
        </>}
      </div>
      <footer><span>RITS FOUNDATION <b>v0.1.0</b></span><span>BUILT FOR WINDOWS <span className="footer-sep">•</span> OPEN SOURCE</span></footer>
    </section>
  </main>;
}
