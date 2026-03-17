// src/pages/IPO.jsx
import { useState, useEffect } from "react";

const TABS = ["Open", "Upcoming", "SME", "Closed", "Listed"];
const TAB_ENDPOINTS = {
  Open: "/api/ipo/open",
  Upcoming: "/api/ipo/upcoming",
  SME: "/api/ipo/sme",
  Closed: "/api/ipo/closed",
  Listed: "/api/ipo/listed",
};

function GmpBadge({ gmp }) {
  if (!gmp) return null;
  const val = gmp.gmp || 0;
  const gain = gmp.listing_gain_pct || 0;
  const color = val > 20 || gain > 15 ? "#00e5a0" : val > 0 ? "#5b8dee" : "var(--muted)";
  return (
    <span style={{ display:"inline-flex", alignItems:"center", gap:4, padding:"2px 8px",
      borderRadius:999, fontSize:11, fontWeight:700, border:`1px solid ${color}`, color }}>
      GMP ₹{val}{gain > 0 && <span style={{opacity:0.75}}> · {gain}%</span>}
    </span>
  );
}

function TypeBadge({ type }) {
  const isSme = type === "SME";
  return (
    <span style={{ fontSize:11, fontWeight:600, padding:"2px 8px", borderRadius:4,
      background: isSme ? "rgba(91,141,238,0.15)" : "rgba(0,229,160,0.1)",
      color: isSme ? "var(--accent3)" : "var(--accent)" }}>
      {type || "Mainboard"}
    </span>
  );
}

function StatBox({ label, value }) {
  if (!value) return null;
  return (
    <div style={{ background:"var(--surface)", border:"1px solid var(--border)",
      borderRadius:6, padding:"6px 10px" }}>
      <div style={{ fontSize:10, color:"var(--muted)", marginBottom:2 }}>{label}</div>
      <div style={{ fontSize:12, fontWeight:700, color:"var(--text)" }}>{value}</div>
    </div>
  );
}

function IpoCard({ ipo, tab, onVerdict }) {
  const name = ipo.companyName || ipo.name || ipo.company || "—";

  if (tab === "SME") {
    return (
      <div style={{ background:"var(--card)", border:"1px solid var(--border)",
        borderRadius:12, padding:16, display:"flex", flexDirection:"column", gap:10 }}>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:8 }}>
          <div>
            <div style={{ fontWeight:700, color:"var(--text)", fontSize:14, lineHeight:1.3 }}>{name}</div>
            <div style={{ fontSize:11, color:"var(--muted)", marginTop:3 }}>{ipo.dates || "—"}</div>
          </div>
          <TypeBadge type="SME" />
        </div>
        <div style={{ display:"flex", flexWrap:"wrap", gap:6 }}>
          {ipo.price_band && (
            <span style={{ fontSize:11, background:"var(--surface)", border:"1px solid var(--border)",
              borderRadius:4, padding:"3px 8px", color:"var(--text)" }}>
              ₹{ipo.price_band}
            </span>
          )}
          <span style={{ fontSize:11, fontWeight:700, padding:"3px 8px", borderRadius:4,
            background: (ipo.gmp||0) > 0 ? "rgba(0,229,160,0.1)" : "var(--surface)",
            color: (ipo.gmp||0) > 0 ? "var(--accent)" : "var(--muted)",
            border:`1px solid ${(ipo.gmp||0) > 0 ? "var(--accent)" : "var(--border)"}` }}>
            GMP ₹{ipo.gmp || 0}{ipo.listing_gain_pct > 0 && ` (${ipo.listing_gain_pct}%)`}
          </span>
          {ipo.sentiment && (
            <span style={{ fontSize:11, padding:"3px 8px", borderRadius:4,
              background:"rgba(245,197,24,0.1)", color:"var(--warn)",
              border:"1px solid rgba(245,197,24,0.3)" }}>
              {ipo.sentiment}
            </span>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ background:"var(--card)", border:"1px solid var(--border)",
      borderRadius:12, padding:16, display:"flex", flexDirection:"column", gap:10 }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:8 }}>
        <div>
          <div style={{ fontWeight:700, color:"var(--text)", fontSize:14, lineHeight:1.3 }}>{name}</div>
          {ipo.symbol && <div style={{ fontSize:11, color:"var(--muted)", marginTop:2, fontFamily:"var(--mono)" }}>{ipo.symbol}</div>}
        </div>
        <TypeBadge type={ipo.type} />
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:6 }}>
        <StatBox label="Price" value={ipo.issuePrice || ipo.priceRange ? `₹${ipo.issuePrice || ipo.priceRange}` : null} />
        <StatBox label="Opens" value={ipo.issueStartDate || ipo.ipoStartDate} />
        <StatBox label="Closes" value={ipo.issueEndDate || ipo.ipoEndDate} />
        {ipo.listingDate && <StatBox label="Listed" value={ipo.listingDate} />}
        {ipo.issueSize && <StatBox label="Size" value={ipo.issueSize} />}
        {ipo.subscriptionTimes > 0 && (
          <div style={{ background:"rgba(0,229,160,0.08)", border:"1px solid rgba(0,229,160,0.3)",
            borderRadius:6, padding:"6px 10px", gridColumn:"1/-1" }}>
            <div style={{ fontSize:10, color:"var(--accent)", marginBottom:2 }}>Subscribed</div>
            <div style={{ fontSize:14, fontWeight:800, color:"var(--accent)" }}>{ipo.subscriptionTimes}x</div>
          </div>
        )}
      </div>

      {ipo.gmp && (
        <div style={{ display:"flex", alignItems:"center", gap:8 }}>
          <GmpBadge gmp={ipo.gmp} />
          {ipo.gmp.sentiment && <span style={{ fontSize:11, color:"var(--muted)" }}>{ipo.gmp.sentiment}</span>}
        </div>
      )}

      {(tab === "Open" || tab === "Upcoming") && (
        <button onClick={() => onVerdict(name)} style={{
          width:"100%", padding:"8px 0", borderRadius:8, border:"none", cursor:"pointer",
          background:"linear-gradient(135deg,#5b8dee,#00e5a0)", color:"#000",
          fontWeight:700, fontSize:12, letterSpacing:0.5 }}>
          ✨ AI Verdict
        </button>
      )}
    </div>
  );
}

function VerdictModal({ company, onClose }) {
  const [verdict, setVerdict] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/ipo/verdict/${encodeURIComponent(company)}`)
      .then((r) => r.json())
      .then((data) => setVerdict(data))
      .catch(() => setVerdict({ verdict: "Could not fetch AI verdict.", company }))
      .finally(() => setLoading(false));
  }, [company]);

  return (
    <div style={{ position:"fixed", inset:0, background:"rgba(0,0,0,0.7)", zIndex:50,
      display:"flex", alignItems:"flex-end", justifyContent:"center", padding:16 }}>
      <div style={{ background:"var(--card)", border:"1px solid var(--border)",
        borderRadius:16, width:"100%", maxWidth:480, boxShadow:"0 20px 60px rgba(0,0,0,0.5)" }}>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center",
          padding:"14px 16px", borderBottom:"1px solid var(--border)" }}>
          <span style={{ fontWeight:700, color:"var(--text)", fontSize:14 }}>✨ AI Verdict — {company}</span>
          <button onClick={onClose} style={{ background:"none", border:"none", color:"var(--muted)",
            fontSize:22, cursor:"pointer", lineHeight:1 }}>×</button>
        </div>
        <div style={{ padding:16 }}>
          {loading ? (
            <div style={{ display:"flex", alignItems:"center", gap:10, color:"var(--muted)",
              fontSize:13, padding:"20px 0", justifyContent:"center" }}>
              <div style={{ width:16, height:16, border:"2px solid var(--accent3)",
                borderTopColor:"transparent", borderRadius:"50%",
                animation:"spin 0.8s linear infinite" }} />
              Analysing IPO...
            </div>
          ) : (
            <>
              {verdict?.gmp && <div style={{marginBottom:10}}><GmpBadge gmp={verdict.gmp} /></div>}
              <div style={{ fontSize:13, color:"var(--text)", whiteSpace:"pre-wrap", lineHeight:1.7 }}>
                {verdict?.verdict}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function IPO() {
  const [activeTab, setActiveTab] = useState("Open");
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [verdictCompany, setVerdictCompany] = useState(null);

  useEffect(() => {
    if (data[activeTab]) return;
    setLoading(true);
    setError(null);
    fetch(TAB_ENDPOINTS[activeTab])
      .then((r) => r.json())
      .then((d) => setData((prev) => ({ ...prev, [activeTab]: d })))
      .catch((err) => setError(err.message || "Failed to load IPO data"))
      .finally(() => setLoading(false));
  }, [activeTab]);

  const ipos = data[activeTab]?.ipos || [];

  return (
    <div style={{ minHeight:"100vh", background:"var(--bg)", padding:"24px 16px" }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ maxWidth:900, margin:"0 auto" }}>

        <div style={{ marginBottom:24 }}>
          <h1 style={{ fontSize:26, fontWeight:800, color:"var(--text)", margin:0 }}>📋 IPO Tracker</h1>
          <p style={{ fontSize:13, color:"var(--muted)", marginTop:6 }}>
            Live IPO data · GMP from grey market · AI verdicts powered by Groq
          </p>
        </div>

        {/* Tabs */}
        <div style={{ display:"flex", gap:4, background:"var(--surface)", borderRadius:12,
          padding:4, border:"1px solid var(--border)", marginBottom:24, overflowX:"auto" }}>
          {TABS.map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              flex:1, minWidth:"fit-content", padding:"8px 14px", borderRadius:8, border:"none",
              cursor:"pointer", fontSize:13, fontWeight:600, whiteSpace:"nowrap", transition:"all 0.2s",
              background: activeTab === tab ? "var(--accent3)" : "transparent",
              color: activeTab === tab ? "#fff" : "var(--muted)" }}>
              {tab === "SME" ? "🏭 SME" : tab}
            </button>
          ))}
        </div>

        {/* SME note */}
        {activeTab === "SME" && (
          <div style={{ marginBottom:16, background:"rgba(245,197,24,0.08)",
            border:"1px solid rgba(245,197,24,0.3)", borderRadius:8,
            padding:"8px 12px", fontSize:12, color:"var(--warn)" }}>
            📌 SME IPO data sourced from ipowatch.in grey market tracker. NSE API has no SME IPO listing endpoint.
          </div>
        )}

        {data[activeTab]?.updated_at && (
          <div style={{ marginBottom:12, fontSize:11, color:"var(--muted)" }}>
            GMP updated: {data[activeTab].updated_at} · Unofficial grey market data
          </div>
        )}

        {loading && (
          <div style={{ display:"flex", alignItems:"center", justifyContent:"center",
            gap:10, padding:"64px 0", color:"var(--muted)" }}>
            <div style={{ width:20, height:20, border:"2px solid var(--accent3)",
              borderTopColor:"transparent", borderRadius:"50%",
              animation:"spin 0.8s linear infinite" }} />
            Loading IPO data...
          </div>
        )}

        {error && (
          <div style={{ background:"rgba(255,71,87,0.1)", border:"1px solid rgba(255,71,87,0.3)",
            borderRadius:10, padding:"12px 16px", color:"var(--danger)", fontSize:13 }}>
            ⚠️ {error}
          </div>
        )}

        {!loading && !error && (
          ipos.length === 0 ? (
            <div style={{ textAlign:"center", padding:"64px 0", color:"var(--muted)" }}>
              <div style={{ fontSize:40, marginBottom:12 }}>📭</div>
              <div style={{ fontWeight:600, fontSize:15 }}>No IPOs found in this category</div>
              <div style={{ fontSize:13, marginTop:6 }}>Check back later for updates</div>
            </div>
          ) : (
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(260px,1fr))", gap:16 }}>
              {ipos.map((ipo, i) => (
                <IpoCard key={i} ipo={ipo} tab={activeTab} onVerdict={(name) => setVerdictCompany(name)} />
              ))}
            </div>
          )
        )}

        <div style={{ marginTop:32, fontSize:11, color:"var(--muted)", textAlign:"center" }}>
          ⚠️ GMP is unofficial grey market data for informational purposes only. Not investment advice.
        </div>
      </div>

      {verdictCompany && (
        <VerdictModal company={verdictCompany} onClose={() => setVerdictCompany(null)} />
      )}
    </div>
  );
}
