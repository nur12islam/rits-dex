import { FormEvent, useEffect, useState } from "react";
import { Activity, ArrowUpRight, Command, Cpu, Mic, ShieldCheck, Sparkles, Terminal } from "lucide-react";

type Result = { source: string; message: string; proposal?: { action_id: string; arguments: Record<string, unknown>; description: string } | null };

const API = "http://127.0.0.1:8765";

export default function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [online, setOnline] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(API + "/health").then(r => r.ok ? r.json() : Promise.reject()).then(() => setOnline(true)).catch(() => setOnline(false));
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
    } catch {
      setResult({ source: "offline", message: "Can't reach the local RITS core. Start the backend using the setup instructions in the repository." });
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
      <div className="nav-item active"><Command size={17} /> Assistant <span className="nav-dot" /></div>
      <div className="nav-item muted"><Activity size={17} /> Activity <em>SOON</em></div>
      <div className="nav-item muted"><Cpu size={17} /> Integrations <em>SOON</em></div>
      <div className="sidebar-bottom"><ShieldCheck size={16} /><span>Local-first by design</span></div>
    </aside>
    <section className="main-panel">
      <header className="topbar"><div className="breadcrumb">Workspace <span>/</span> <b>Assistant</b></div><div className="connection"><i className={online ? "online" : ""} />{online ? "LOCAL CORE CONNECTED" : "CORE OFFLINE"}</div></header>
      <div className="content">
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
      </div>
      <footer><span>RITS FOUNDATION <b>v0.1.0</b></span><span>BUILT FOR WINDOWS <span className="footer-sep">•</span> OPEN SOURCE</span></footer>
    </section>
  </main>;
}
