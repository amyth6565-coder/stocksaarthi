import { useState, useEffect, useRef } from 'react'
import { searchStocks } from '../utils/api'

const QUICK = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'BAJFINANCE', 'ITC']

export default function SearchBar({ onAnalyse, loading }) {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSugg, setShowSugg] = useState(false)
  const [exchange, setExchange] = useState('NSE')
  const debounceRef = useRef(null)

  useEffect(() => {
    clearTimeout(debounceRef.current)
    if (!query) { setSuggestions([]); return }
    debounceRef.current = setTimeout(async () => {
      setSuggestions(await searchStocks(query))
      setShowSugg(true)
    }, 250)
  }, [query])

  function submit(sym) {
    const s = (sym || query).toUpperCase().trim()
    if (!s) return
    setQuery(s); setShowSugg(false); onAnalyse(s, exchange)
  }

  return (
    <div style={{ width: '100%', maxWidth: 640, margin: '0 auto' }}>
      <style>{`
        .search-row { display: flex; }
        .analyse-btn { padding: 14px 22px; font-size: 0.82rem; }
        @media (max-width: 480px) {
          .analyse-btn { padding: 14px 14px; font-size: 0.75rem; }
          .quick-row { gap: 5px !important; }
          .quick-btn { font-size: 0.58rem !important; padding: 4px 7px !important; }
        }
      `}</style>

      {/* Exchange toggle */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 10, justifyContent: 'center' }}>
        {['NSE', 'BSE'].map(ex => (
          <button key={ex} onClick={() => setExchange(ex)} style={{
            fontFamily: 'var(--mono)', fontSize: '0.7rem', letterSpacing: 2,
            padding: '5px 18px', border: '1px solid',
            borderColor: exchange === ex ? 'var(--accent)' : 'var(--border)',
            background: exchange === ex ? 'rgba(0,229,160,0.1)' : 'transparent',
            color: exchange === ex ? 'var(--accent)' : 'var(--muted)',
            cursor: 'pointer', borderRadius: 2,
          }}>{ex}</button>
        ))}
      </div>

      {/* Search input */}
      <div className="search-row" style={{ position: 'relative' }}>
        <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center' }}>
          <span style={{ position: 'absolute', left: 12, color: 'var(--muted)', pointerEvents: 'none', fontSize: '1rem' }}>⌕</span>
          <input
            value={query}
            onChange={e => setQuery(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && submit()}
            onFocus={() => suggestions.length && setShowSugg(true)}
            onBlur={() => setTimeout(() => setShowSugg(false), 150)}
            placeholder="RELIANCE, TCS, INFY..."
            disabled={loading}
            style={{
              width: '100%', background: 'var(--card)',
              border: '1px solid var(--border)', borderRight: 'none',
              outline: 'none', padding: '14px 16px 14px 36px',
              fontFamily: 'var(--mono)', fontSize: '0.88rem',
              color: 'var(--text)', borderRadius: '3px 0 0 3px',
            }}
          />
          {showSugg && suggestions.length > 0 && (
            <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, background: 'var(--card)', border: '1px solid var(--border)', borderTop: 'none', borderRadius: '0 0 3px 3px', zIndex: 100 }}>
              {suggestions.map(s => (
                <div key={s.symbol} onMouseDown={() => submit(s.symbol)}
                  style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', cursor: 'pointer' }}
                  onMouseEnter={e => e.currentTarget.style.background = '#1a2535'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                  <span style={{ fontFamily: 'var(--mono)', fontWeight: 700, fontSize: '0.78rem', color: 'var(--accent)', minWidth: 80 }}>{s.symbol}</span>
                  <span style={{ fontSize: '0.78rem', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.name}</span>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: '0.62rem', color: 'var(--muted)', display: 'none' }} className="sector-tag">{s.sector}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        <button className="analyse-btn" onClick={() => submit()} disabled={loading || !query}
          style={{
            background: loading || !query ? 'var(--border)' : 'var(--accent)',
            color: loading || !query ? 'var(--muted)' : '#000',
            border: 'none', fontFamily: 'var(--sans)', fontWeight: 700,
            cursor: loading || !query ? 'not-allowed' : 'pointer',
            letterSpacing: 1, textTransform: 'uppercase',
            borderRadius: '0 3px 3px 0', whiteSpace: 'nowrap',
          }}>
          {loading ? '...' : 'Analyse →'}
        </button>
      </div>

      {/* Quick picks */}
      <div className="quick-row" style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 10, flexWrap: 'wrap', justifyContent: 'center' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: '0.62rem', color: 'var(--muted)' }}>Try:</span>
        {QUICK.map(s => (
          <button key={s} className="quick-btn" onClick={() => submit(s)} disabled={loading}
            style={{ fontFamily: 'var(--mono)', fontSize: '0.62rem', padding: '4px 9px', border: '1px solid var(--border)', background: 'transparent', color: 'var(--muted)', cursor: 'pointer', borderRadius: 2 }}>
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}
