import { useRef, useEffect } from 'react'
import SearchBar from '../components/SearchBar'
import VerdictCard from '../components/VerdictCard'
import PriceChart from '../components/PriceChart'
import TechnicalPanel from '../components/TechnicalPanel'
import FundamentalsPanel from '../components/FundamentalsPanel'
import { useStockAnalysis } from '../hooks/useStockAnalysis'

export default function Dashboard() {
  const { data, loading, error, analyse } = useStockAnalysis()
  const resultRef = useRef(null)
  useEffect(() => {
    if (data && resultRef.current) resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [data])
  const verdict = data?.ai_verdict?.verdict

  return (
    <div style={{ minHeight: '100vh', position: 'relative', zIndex: 1 }}>
      <style>{`
        .top-grid { display: grid; grid-template-columns: 360px 1fr; gap: 16px; margin-bottom: 16px; }
        .bottom-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
        .company-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
        @media (max-width: 900px) {
          .top-grid { grid-template-columns: 1fr !important; }
          .bottom-grid { grid-template-columns: 1fr !important; }
        }
        @media (max-width: 600px) {
          .company-header { flex-direction: column; gap: 12px; }
          .hero-pad { padding: 28px 16px 24px !important; }
          .main-pad { padding: 0 16px 80px !important; }
        }
      `}</style>

      {/* HERO */}
      <div className="hero-pad" style={{ maxWidth: 1200, margin: '0 auto', padding: '48px 16px 36px', textAlign: 'center' }}>
        <div style={{ display: 'inline-block', fontFamily: 'var(--mono)', fontSize: '0.65rem', color: 'var(--accent)', background: 'rgba(0,229,160,0.08)', border: '1px solid rgba(0,229,160,0.2)', padding: '4px 14px', borderRadius: 2, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 16 }}>
          Technical + Fundamental + AI
        </div>
        <h1 style={{ fontSize: 'clamp(1.8rem, 5vw, 3.2rem)', fontWeight: 800, lineHeight: 1.1, letterSpacing: -1, marginBottom: 12 }}>
          Should you <span style={{ color: 'var(--accent)' }}>buy</span> this<br />Indian stock?
        </h1>
        <p style={{ fontFamily: 'var(--mono)', color: 'var(--muted)', fontSize: '0.82rem', marginBottom: 28 }}>
          // Enter any NSE/BSE symbol for instant AI verdict
        </p>
        <SearchBar onAnalyse={analyse} loading={loading} />
      </div>

      {/* MAIN */}
      <div className="main-pad" style={{ maxWidth: 1200, margin: '0 auto', padding: '0 16px 80px' }}>

        {error && (
          <div style={{ background: 'rgba(255,71,87,0.08)', border: '1px solid rgba(255,71,87,0.3)', borderRadius: 4, padding: '14px 18px', fontFamily: 'var(--mono)', fontSize: '0.8rem', color: 'var(--danger)', marginBottom: 24 }}>⚠ {error}</div>
        )}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 4, padding: '20px 24px', marginBottom: 24 }}>
            <div style={{ width: 28, height: 28, flexShrink: 0, border: '3px solid var(--border)', borderTop: '3px solid var(--accent)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: 4 }}>Analysing stock...</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: '0.68rem', color: 'var(--muted)', lineHeight: 1.6 }}>Fetching data → Calculating indicators → AI verdict</div>
            </div>
          </div>
        )}

        {data && !loading && (
          <div ref={resultRef}>
            <div className="company-header">
              <div>
                <div style={{ fontSize: 'clamp(1.2rem, 3vw, 1.6rem)', fontWeight: 800, letterSpacing: -0.5, marginBottom: 8 }}>{data.company?.name}</div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {[
                    { v: `${data.symbol}.${data.exchange}`, c: 'var(--accent)', bg: 'rgba(0,229,160,0.1)' },
                    { v: data.company?.sector, c: 'var(--muted)', bg: 'var(--surface)' },
                    { v: data.company?.industry, c: 'var(--muted)', bg: 'var(--surface)' },
                  ].map(({ v, c, bg }, i) => v && (
                    <span key={i} style={{ fontFamily: 'var(--mono)', fontSize: '0.68rem', color: c, background: bg, padding: '3px 10px', borderRadius: 2 }}>{v}</span>
                  ))}
                </div>
              </div>
              {verdict && (
                <div style={{
                  fontWeight: 800, fontSize: '1.3rem', letterSpacing: 1,
                  color: { BUY: '#00e5a0', HOLD: '#f5c518', AVOID: '#ff4757' }[verdict],
                  background: { BUY: 'rgba(0,229,160,0.1)', HOLD: 'rgba(245,197,24,0.1)', AVOID: 'rgba(255,71,87,0.1)' }[verdict],
                  border: `1px solid ${{ BUY: 'rgba(0,229,160,0.3)', HOLD: 'rgba(245,197,24,0.3)', AVOID: 'rgba(255,71,87,0.3)' }[verdict]}`,
                  padding: '8px 20px', borderRadius: 4, whiteSpace: 'nowrap',
                }}>{verdict}</div>
              )}
            </div>

            <div className="top-grid">
              <VerdictCard ai={data.ai_verdict} price={data.price} />
              <PriceChart chartData={data.technicals?.chart_data} verdict={verdict} />
            </div>
            <div className="bottom-grid">
              <TechnicalPanel tech={data.technicals} />
              <FundamentalsPanel fundamentals={data.fundamentals} fundScore={data.fundamental_score} />
            </div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: '0.62rem', color: 'var(--muted)', textAlign: 'center', padding: '12px', border: '1px solid var(--border)', borderRadius: 3 }}>
              ⚠ For educational purposes only. Not financial advice.
            </div>
          </div>
        )}

        {!data && !loading && !error && (
          <div style={{ textAlign: 'center', padding: '48px 16px' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: 16 }}>📊</div>
            <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: 8 }}>Enter a stock symbol above</div>
            <div style={{ fontFamily: 'var(--mono)', color: 'var(--muted)', fontSize: '0.78rem' }}>Try RELIANCE, TCS, HDFCBANK, INFY or any NSE symbol</div>
          </div>
        )}
      </div>

      <footer style={{ borderTop: '1px solid var(--border)', padding: '16px 0', textAlign: 'center' }}>
        <p style={{ fontFamily: 'var(--mono)', fontSize: '0.62rem', color: 'var(--muted)' }}>StockSaarthi · yfinance + Groq + FastAPI · Educational use only</p>
      </footer>
    </div>
  )
}
