// src/pages/IPO.jsx
// IPO Tracker with 5 tabs: Open | Upcoming | SME | Closed | Listed
// GMP badge shown on all cards where available

import { useState, useEffect } from "react";
import api from "../utils/api";

const TABS = ["Open", "Upcoming", "SME", "Closed", "Listed"];

const TAB_ENDPOINTS = {
  Open: "/api/ipo/open",
  Upcoming: "/api/ipo/upcoming",
  SME: "/api/ipo/sme",
  Closed: "/api/ipo/closed",
  Listed: "/api/ipo/listed",
};

// ── GMP Badge ────────────────────────────────────────────────────────────────
function GmpBadge({ gmp }) {
  if (!gmp) return null;
  const val = gmp.gmp || 0;
  const gain = gmp.listing_gain_pct || 0;
  const color =
    val > 20 || gain > 15
      ? "bg-green-100 text-green-800 border-green-300"
      : val > 0
      ? "bg-blue-100 text-blue-800 border-blue-300"
      : "bg-gray-100 text-gray-500 border-gray-200";

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${color}`}
      title="Grey Market Premium (unofficial)"
    >
      GMP ₹{val}
      {gain > 0 && <span className="opacity-75">· {gain}%</span>}
    </span>
  );
}

// ── Type Badge ────────────────────────────────────────────────────────────────
function TypeBadge({ type }) {
  const isSme = type === "SME";
  return (
    <span
      className={`text-xs font-medium px-2 py-0.5 rounded ${
        isSme ? "bg-purple-100 text-purple-700" : "bg-blue-100 text-blue-700"
      }`}
    >
      {type || "Mainboard"}
    </span>
  );
}

// ── IPO Card ─────────────────────────────────────────────────────────────────
function IpoCard({ ipo, tab, onVerdict }) {
  const name =
    ipo.companyName || ipo.name || ipo.company || "—";

  // SME tab comes from GMP scraper — different shape
  if (tab === "SME") {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-sm leading-tight">{name}</h3>
            <p className="text-xs text-gray-500 mt-0.5">{ipo.dates || "—"}</p>
          </div>
          <TypeBadge type="SME" />
        </div>

        <div className="flex flex-wrap gap-2 mt-3">
          <div className="text-xs bg-gray-50 rounded px-2 py-1">
            <span className="text-gray-500">Price Band: </span>
            <span className="font-medium text-gray-800">
              {ipo.price_band ? `₹${ipo.price_band}` : "—"}
            </span>
          </div>

          <div
            className={`text-xs rounded px-2 py-1 font-semibold ${
              (ipo.gmp || 0) > 0
                ? "bg-green-100 text-green-700"
                : "bg-gray-100 text-gray-500"
            }`}
          >
            GMP: ₹{ipo.gmp || 0}
            {ipo.listing_gain_pct > 0 && (
              <span className="ml-1">({ipo.listing_gain_pct}%)</span>
            )}
          </div>

          {ipo.sentiment && (
            <div className="text-xs bg-yellow-50 text-yellow-700 rounded px-2 py-1">
              {ipo.sentiment}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Standard NSE IPO card
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight">{name}</h3>
          {ipo.symbol && (
            <p className="text-xs text-gray-400 mt-0.5 font-mono">{ipo.symbol}</p>
          )}
        </div>
        <TypeBadge type={ipo.type} />
      </div>

      <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
        {(ipo.issuePrice || ipo.priceRange) && (
          <div className="bg-gray-50 rounded px-2 py-1.5">
            <span className="text-gray-500 block">Price</span>
            <span className="font-semibold text-gray-800">
              ₹{ipo.issuePrice || ipo.priceRange}
            </span>
          </div>
        )}
        {(ipo.issueStartDate || ipo.ipoStartDate) && (
          <div className="bg-gray-50 rounded px-2 py-1.5">
            <span className="text-gray-500 block">Opens</span>
            <span className="font-semibold text-gray-800">
              {ipo.issueStartDate || ipo.ipoStartDate}
            </span>
          </div>
        )}
        {(ipo.issueEndDate || ipo.ipoEndDate) && (
          <div className="bg-gray-50 rounded px-2 py-1.5">
            <span className="text-gray-500 block">Closes</span>
            <span className="font-semibold text-gray-800">
              {ipo.issueEndDate || ipo.ipoEndDate}
            </span>
          </div>
        )}
        {ipo.listingDate && (
          <div className="bg-gray-50 rounded px-2 py-1.5">
            <span className="text-gray-500 block">Listed</span>
            <span className="font-semibold text-gray-800">{ipo.listingDate}</span>
          </div>
        )}
        {ipo.subscriptionTimes > 0 && (
          <div className="bg-indigo-50 rounded px-2 py-1.5 col-span-2">
            <span className="text-indigo-500 block">Subscribed</span>
            <span className="font-bold text-indigo-700">{ipo.subscriptionTimes}x</span>
          </div>
        )}
        {ipo.issueSize && (
          <div className="bg-gray-50 rounded px-2 py-1.5">
            <span className="text-gray-500 block">Size</span>
            <span className="font-semibold text-gray-800">₹{ipo.issueSize} Cr</span>
          </div>
        )}
      </div>

      {/* GMP badge */}
      {ipo.gmp && (
        <div className="mt-3 flex items-center gap-2">
          <GmpBadge gmp={ipo.gmp} />
          {ipo.gmp.sentiment && (
            <span className="text-xs text-gray-400">{ipo.gmp.sentiment}</span>
          )}
        </div>
      )}

      {/* AI Verdict button */}
      {(tab === "Open" || tab === "Upcoming") && (
        <button
          onClick={() => onVerdict(name)}
          className="mt-3 w-full text-xs bg-indigo-600 hover:bg-indigo-700 text-white py-1.5 rounded-lg font-medium transition-colors"
        >
          ✨ AI Verdict
        </button>
      )}
    </div>
  );
}

// ── Verdict Modal ─────────────────────────────────────────────────────────────
function VerdictModal({ company, onClose }) {
  const [verdict, setVerdict] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.get(`/api/ipo/verdict/${encodeURIComponent(company)}`);
        setVerdict(res.data);
      } catch {
        setVerdict({ verdict: "Could not fetch AI verdict. Please try again.", company });
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [company]);

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="font-bold text-gray-800 text-sm">
            ✨ AI Verdict — {company}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ×
          </button>
        </div>
        <div className="p-4">
          {loading ? (
            <div className="flex items-center gap-2 text-gray-500 text-sm py-4 justify-center">
              <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
              Analysing IPO...
            </div>
          ) : (
            <>
              {verdict?.gmp && <GmpBadge gmp={verdict.gmp} />}
              <div className="mt-3 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                {verdict?.verdict}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Main IPO Page ─────────────────────────────────────────────────────────────
export default function IPO() {
  const [activeTab, setActiveTab] = useState("Open");
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [verdictCompany, setVerdictCompany] = useState(null);

  useEffect(() => {
    if (data[activeTab]) return; // already cached
    setLoading(true);
    setError(null);
    api
      .get(TAB_ENDPOINTS[activeTab])
      .then((res) => {
        setData((prev) => ({ ...prev, [activeTab]: res.data }));
      })
      .catch((err) => {
        setError(err.message || "Failed to load IPO data");
      })
      .finally(() => setLoading(false));
  }, [activeTab]);

  const ipos =
    data[activeTab]?.ipos ||
    data[activeTab]?.mainboard ||  // GMP endpoint shape
    [];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-6">

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">📋 IPO Tracker</h1>
          <p className="text-sm text-gray-500 mt-1">
            Live IPO data · GMP from grey market · AI verdicts powered by Groq
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-white rounded-xl p-1 border border-gray-200 shadow-sm mb-6 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 min-w-fit px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                activeTab === tab
                  ? "bg-indigo-600 text-white shadow"
                  : "text-gray-500 hover:text-gray-800 hover:bg-gray-50"
              }`}
            >
              {tab === "SME" ? "🏭 SME" : tab}
            </button>
          ))}
        </div>

        {/* SME source note */}
        {activeTab === "SME" && (
          <div className="mb-4 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-xs text-amber-700">
            📌 SME IPO data sourced from grey market tracker (ipowatch.in). Includes GMP + upcoming SME IPOs not available via NSE API.
          </div>
        )}

        {/* GMP disclaimer */}
        {data[activeTab]?.updated_at && (
          <div className="mb-4 text-xs text-gray-400">
            GMP data updated: {data[activeTab].updated_at} · Grey market data is unofficial
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-16 text-gray-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
            Loading IPO data...
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* IPO Cards Grid */}
        {!loading && !error && (
          <>
            {ipos.length === 0 ? (
              <div className="text-center py-16 text-gray-400">
                <div className="text-4xl mb-3">📭</div>
                <p className="font-medium">No IPOs found in this category</p>
                <p className="text-sm mt-1">Check back later for updates</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {ipos.map((ipo, i) => (
                  <IpoCard
                    key={i}
                    ipo={ipo}
                    tab={activeTab}
                    onVerdict={(name) => setVerdictCompany(name)}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* GMP Disclaimer */}
        <div className="mt-8 text-xs text-gray-400 text-center">
          ⚠️ GMP data is from the unofficial grey market and is for informational purposes only.
          It is not a reliable predictor of listing price. Always do your own research.
        </div>
      </div>

      {/* Verdict Modal */}
      {verdictCompany && (
        <VerdictModal
          company={verdictCompany}
          onClose={() => setVerdictCompany(null)}
        />
      )}
    </div>
  );
}