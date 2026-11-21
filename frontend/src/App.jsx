import { useState, useRef, useEffect } from "react";
import "./App.css";

const WELCOME =
  "Hi! I'm your IT Helpdesk assistant. Describe your issue and I will troubleshoot it, run a safe fix, or escalate it to the L2 support team.";

const CATS = ["All", "Network", "Access", "Hardware", "Software", "Security"];

const SUGGESTIONS = [
  { cat: "Network", icon: "🔐", label: "VPN not connecting", text: "My VPN is not connecting" },
  { cat: "Network", icon: "📶", label: "Wi-Fi problem", text: "Wi-Fi is connected but no internet" },
  { cat: "Access", icon: "🔑", label: "Forgot password", text: "I forgot my password" },
  { cat: "Access", icon: "🔒", label: "Account locked", text: "My account is locked out" },
  { cat: "Access", icon: "📱", label: "MFA / OTP issue", text: "I am not receiving the OTP for MFA" },
  { cat: "Hardware", icon: "🖨️", label: "Printer offline", text: "Printer shows offline and jobs are stuck" },
  { cat: "Hardware", icon: "🐢", label: "Slow laptop", text: "My laptop is very slow" },
  { cat: "Hardware", icon: "💻", label: "Blue screen", text: "My laptop shows a blue screen error" },
  { cat: "Hardware", icon: "💾", label: "Disk space full", text: "My disk is almost full, low storage warning" },
  { cat: "Software", icon: "📧", label: "Outlook not opening", text: "Outlook is not opening" },
  { cat: "Software", icon: "🎙️", label: "Teams mic issue", text: "Teams microphone is not working" },
  { cat: "Software", icon: "📦", label: "Install software", text: "I need to install new software" },
  { cat: "Security", icon: "🛡️", label: "Phishing email", text: "I clicked a phishing link in an email" },
  { cat: "Security", icon: "🦠", label: "Malware suspected", text: "I think my computer has malware" },
  { cat: "Software", icon: "📷", label: "Camera not detected", text: "My camera is not detected in Zoom" },
];

const KB = [
  { cat: "Network", icon: "🔐", title: "VPN not connecting", desc: "Client errors, failed logins and dropped connections", ask: "My VPN is not connecting" },
  { cat: "Network", icon: "📶", title: "Wi-Fi not connecting or slow", desc: "No internet, weak signal, adapter and DNS fixes", ask: "Wi-Fi is connected but no internet" },
  { cat: "Access", icon: "🔑", title: "Forgot or expired password", desc: "Self-service reset and temporary password", ask: "I forgot my password" },
  { cat: "Access", icon: "🔒", title: "Account locked out", desc: "Wait, check saved passwords, request unlock", ask: "My account is locked out" },
  { cat: "Access", icon: "📱", title: "MFA or OTP not working", desc: "Phone time, signal and MFA reset rules", ask: "I am not receiving the OTP for MFA" },
  { cat: "Hardware", icon: "🖨️", title: "Printer not printing", desc: "Stuck queue, offline printer, paper jam", ask: "Printer shows offline and jobs are stuck" },
  { cat: "Hardware", icon: "🐢", title: "Laptop running slow", desc: "Startup apps, disk space and updates", ask: "My laptop is very slow" },
  { cat: "Hardware", icon: "💻", title: "Blue screen (BSOD)", desc: "Stop codes, drivers and safe mode", ask: "My laptop shows a blue screen error" },
  { cat: "Hardware", icon: "💾", title: "Disk full or low storage", desc: "Cleanup, Storage Sense, move large files", ask: "My disk is almost full, low storage warning" },
  { cat: "Software", icon: "📧", title: "Outlook or email problems", desc: "Safe mode, mailbox size, Office repair", ask: "Outlook is not opening" },
  { cat: "Software", icon: "🎙️", title: "Teams or Zoom audio and video", desc: "Devices, privacy settings and drivers", ask: "Teams microphone is not working" },
  { cat: "Software", icon: "📦", title: "Software installation request", desc: "Approved catalog and request flow", ask: "I need to install new software" },
  { cat: "Security", icon: "🛡️", title: "Phishing or malware", desc: "Immediate steps, always escalated as critical", ask: "I clicked a phishing link in an email" },
];

const NAV = [
  { id: "chat", icon: "chat", label: "Support chat" },
  { id: "dashboard", icon: "dashboard", label: "Dashboard" },
  { id: "kb", icon: "kb", label: "Knowledge base" },
  { id: "about", icon: "about", label: "How it works" },
];

const ICONS = {
  chat: <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />,
  dashboard: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
    </>
  ),
  kb: (
    <>
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </>
  ),
  about: (
    <>
      <circle cx="12" cy="12" r="10" />
      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
    </>
  ),
};

function Icon({ name }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {ICONS[name]}
    </svg>
  );
}

const STEPS = [
  { t: "Classify", d: "Category and priority from keywords, LLM as backup" },
  { t: "Search", d: "Hybrid BM25 and vector search over the KB" },
  { t: "Act", d: "Permitted MCP tools such as password reset" },
  { t: "Resolve", d: "Grounded steps, user confirms the fix" },
  { t: "Escalate", d: "Critical or unresolved goes to L2, report created" },
];

const TECH = [
  "Python", "FastAPI", "LangGraph", "LangChain", "Llama 3.2 (Ollama)", "Agentic RAG",
  "Hybrid search", "ChromaDB", "MCP", "PostgreSQL", "Redis", "Docker", "React",
];

const now = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
const welcomeMsg = () => ({ role: "assistant", text: WELCOME, time: now() });
const fmt = (s) =>
  new Date(s.endsWith("Z") ? s : s + "Z").toLocaleString([], { dateStyle: "medium", timeStyle: "short" });

export default function App() {
  const [page, setPage] = useState("chat");
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState(() => [welcomeMsg()]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [incident, setIncident] = useState(null);
  const [history, setHistory] = useState([]);
  const [cat, setCat] = useState("All");
  const bottomRef = useRef(null);

  function loadHistory() {
    fetch("/api/incidents")
      .then((r) => r.json())
      .then((d) => Array.isArray(d) && setHistory(d))
      .catch(() => {});
  }

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function newChat() {
    setSessionId(crypto.randomUUID());
    setMessages([welcomeMsg()]);
    setIncident(null);
    setInput("");
    setPage("chat");
    loadHistory();
  }

  function askNew(text) {
    const sid = crypto.randomUUID();
    setSessionId(sid);
    setMessages([welcomeMsg()]);
    setIncident(null);
    setPage("chat");
    send(text, sid);
  }

  async function send(text, sid = sessionId) {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;
    setMessages((m) => [...m, { role: "user", text: msg, time: now() }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sid, message: msg }),
      });
      if (!res.ok) throw new Error("Server error " + res.status);
      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", text: data.reply, time: now() }]);
      setIncident({
        id: data.incident_id,
        category: data.category,
        priority: data.priority,
        status: data.status,
      });
      loadHistory();
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "Server not reachable. Please try again. (" + e.message + ")", time: now() },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const showWelcome = messages.length === 1;
  const awaitingFeedback = incident?.status === "open" && !loading;
  const cards = SUGGESTIONS.filter((s) => cat === "All" || s.cat === cat);

  return (
    <div className={"shell" + (page === "chat" ? "" : " wide")}>
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="12" rx="2" />
              <path d="M8 20h8M12 16v4" />
              <path d="M8.5 10l2.5 2.5 4.5-5" />
            </svg>
          </div>
          <div>
            <h1>IT Helpdesk</h1>
            <p>Autonomous Agent</p>
          </div>
        </div>

        <nav className="nav">
          {NAV.map((n) => (
            <button key={n.id} className={page === n.id ? "active" : ""} onClick={() => setPage(n.id)}>
              <Icon name={n.icon} />
              {n.label}
            </button>
          ))}
        </nav>

        <button className="newChat" onClick={newChat}>
          ＋ New chat
        </button>

        <h4>Recent incidents</h4>
        <ul className="history">
          {history.length === 0 && <li className="empty">No incidents yet</li>}
          {history.slice(0, 8).map((h) => (
            <li key={h.id}>
              <a href={"/api/report/" + h.id + "/view"} target="_blank" rel="noreferrer">
                <span className={"dot " + h.status} />
                <span className="hTitle">
                  #{h.id} {h.title}
                </span>
              </a>
            </li>
          ))}
        </ul>

        <div className="stack">LangGraph · Agentic RAG · MCP · FastAPI</div>
      </aside>

      {page === "chat" && (
        <>
          <main className="chatArea">
            <div className="chatHeader">
              <div>
                <h2>Support Chat</h2>
                <span>Describe your IT issue, I will take care of the rest</span>
              </div>
              <div className="online">
                <i /> Agent online
              </div>
            </div>

            <div className="messages">
              {messages.map((m, i) => (
                <div key={i} className={"row " + m.role}>
                  <div className="avatar">{m.role === "user" ? "🧑" : "🤖"}</div>
                  <div className="bubbleWrap">
                    <div className={"bubble " + m.role}>{m.text}</div>
                    <span className="time">{m.time}</span>
                  </div>
                </div>
              ))}

              {showWelcome && (
                <>
                  <div className="chips">
                    {CATS.map((c) => (
                      <button key={c} className={"chip" + (cat === c ? " active" : "")} onClick={() => setCat(c)}>
                        {c}
                      </button>
                    ))}
                  </div>
                  <div className="suggestions">
                    {cards.map((s) => (
                      <button key={s.label} onClick={() => send(s.text)}>
                        <span>{s.icon}</span>
                        {s.label}
                      </button>
                    ))}
                  </div>
                </>
              )}

              {loading && (
                <div className="row assistant">
                  <div className="avatar">🤖</div>
                  <div className="bubble assistant typing">
                    <i />
                    <i />
                    <i />
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {awaitingFeedback && (
              <div className="feedback">
                <span>Did this fix your issue?</span>
                <button className="yes" onClick={() => send("Yes, my issue is resolved")}>
                  ✅ Resolved
                </button>
                <button className="no" onClick={() => send("No, it is still not resolved")}>
                  ❌ Not resolved
                </button>
              </div>
            )}

            <div className="composer">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                placeholder="Describe your issue, e.g. VPN not connecting..."
              />
              <button onClick={() => send()} disabled={loading}>
                Send ➤
              </button>
            </div>
          </main>

          <aside className="details">
            <h3>Incident details</h3>
            {incident ? (
              <div className="card">
                <div className="idRow">
                  <span>Incident</span>
                  <b>#{incident.id}</b>
                </div>
                <div className="field">
                  <label>Category</label>
                  <p className="cap">{incident.category}</p>
                </div>
                <div className="field">
                  <label>Priority</label>
                  <span className={"prio " + incident.priority}>{incident.priority}</span>
                </div>
                <div className="field">
                  <label>Status</label>
                  <span className={"badge " + incident.status}>{incident.status}</span>
                </div>
                <a className="reportBtn" href={"/api/report/" + incident.id + "/view"} target="_blank" rel="noreferrer">
                  📄 View incident report
                </a>
              </div>
            ) : (
              <div className="card placeholder">
                <div className="big">🎫</div>
                <p>No active incident yet.</p>
                <small>Send a message to create one.</small>
              </div>
            )}
          </aside>
        </>
      )}

      {page === "dashboard" && <Dashboard />}
      {page === "kb" && <KnowledgeBase onAsk={askNew} />}
      {page === "about" && <About />}
    </div>
  );
}

function Dashboard() {
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");

  function load() {
    fetch("/api/incidents")
      .then((r) => r.json())
      .then((d) => {
        setRows(Array.isArray(d) ? d : []);
        setErr("");
      })
      .catch(() => setErr("Could not load incidents. Is the API running?"));
  }

  useEffect(() => {
    load();
  }, []);

  const count = (k, v) => rows.filter((r) => r[k] === v).length;
  const total = rows.length;
  const resolved = count("status", "resolved");
  const escalated = count("status", "escalated");
  const open = count("status", "open");
  const rate = total ? Math.round((resolved / total) * 100) : 0;
  const cats = ["network", "access", "hardware", "software", "security", "other"].map((c) => ({
    c,
    n: count("category", c),
  }));
  const max = Math.max(1, ...cats.map((x) => x.n));

  return (
    <section className="page">
      <div className="pageHead">
        <div>
          <h2>Incident dashboard</h2>
          <p>Live view of all incidents handled by the agent</p>
        </div>
        <button className="ghostBtn" onClick={load}>
          ↻ Refresh
        </button>
      </div>

      {err && <p className="errText">{err}</p>}

      <div className="stats">
        <div className="stat">
          <span>Total incidents</span>
          <b>{total}</b>
        </div>
        <div className="stat green">
          <span>Resolved</span>
          <b>{resolved}</b>
        </div>
        <div className="stat red">
          <span>Escalated</span>
          <b>{escalated}</b>
        </div>
        <div className="stat blue">
          <span>Open</span>
          <b>{open}</b>
        </div>
      </div>

      <div className="panelCard">
        <h3>By category (resolution rate {rate}%)</h3>
        {cats.map((x) => (
          <div className="barRow" key={x.c}>
            <label>{x.c}</label>
            <div className="barTrack">
              <div className="barFill" style={{ width: (x.n / max) * 100 + "%" }} />
            </div>
            <b>{x.n}</b>
          </div>
        ))}
      </div>

      <div className="panelCard">
        <h3>Recent incidents</h3>
        <div className="tableWrap">
          <table className="tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th>Issue</th>
                <th>Category</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Created</th>
                <th>Report</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 && (
                <tr>
                  <td colSpan="7">No incidents yet.</td>
                </tr>
              )}
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>#{r.id}</td>
                  <td className="issue">{r.title}</td>
                  <td className="cap">{r.category}</td>
                  <td>
                    <span className={"prio " + r.priority}>{r.priority}</span>
                  </td>
                  <td>
                    <span className={"badge " + r.status}>{r.status}</span>
                  </td>
                  <td>{fmt(r.created_at)}</td>
                  <td>
                    <a href={"/api/report/" + r.id + "/view"} target="_blank" rel="noreferrer">
                      View
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function KnowledgeBase({ onAsk }) {
  const [cat, setCat] = useState("All");
  const [q, setQ] = useState("");
  const list = KB.filter(
    (k) => (cat === "All" || k.cat === cat) && (k.title + " " + k.desc).toLowerCase().includes(q.toLowerCase())
  );

  return (
    <section className="page">
      <div className="pageHead">
        <div>
          <h2>Knowledge base</h2>
          <p>{KB.length} IT articles the agent searches with hybrid RAG</p>
        </div>
        <input className="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search articles..." />
      </div>

      <div className="chips">
        {CATS.map((c) => (
          <button key={c} className={"chip" + (cat === c ? " active" : "")} onClick={() => setCat(c)}>
            {c}
          </button>
        ))}
      </div>

      <div className="kbGrid">
        {list.map((k) => (
          <div className="kbCard" key={k.title}>
            <span className="ic">{k.icon}</span>
            <span className="tagc">{k.cat}</span>
            <h4>{k.title}</h4>
            <p>{k.desc}</p>
            <button onClick={() => onAsk(k.ask)}>Ask the agent →</button>
          </div>
        ))}
      </div>
      {list.length === 0 && <p>No articles match your search.</p>}
    </section>
  );
}

function About() {
  return (
    <section className="page">
      <div className="pageHead">
        <div>
          <h2>How it works</h2>
          <p>From the user message to a resolved or escalated incident</p>
        </div>
      </div>

      <div className="steps">
        {STEPS.map((s, i) => (
          <div className="step" key={s.t}>
            <div className="n">{i + 1}</div>
            <h4>{s.t}</h4>
            <p>{s.d}</p>
          </div>
        ))}
      </div>

      <div className="panelCard" style={{ marginTop: 18 }}>
        <h3>Technology stack</h3>
        <div className="techRow">
          {TECH.map((t) => (
            <span className="tech" key={t}>
              {t}
            </span>
          ))}
        </div>
      </div>

      <div className="panelCard">
        <h3>Agent behaviour</h3>
        <p>
          Security issues are escalated immediately as critical. Other issues are answered only from the knowledge
          base. If the user says the fix did not work, the incident is escalated to the L2 team. Resolved and escalated
          incidents get an automatic incident report.
        </p>
      </div>
    </section>
  );
}