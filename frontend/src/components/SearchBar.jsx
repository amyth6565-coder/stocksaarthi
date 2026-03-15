import { useState, useEffect, useRef } from 'react'
import { searchStocks } from '../utils/api'
const QUICK = ['RELIANCE','TCS','HDFCBANK','INFY','BAJFINANCE','TATASTEEL','ITC','WIPRO']
export default function SearchBar({ onAnalyse, loading }) {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSugg, setShowSugg] = useState(false)
  const [exchange, setExchange] = useState('NSE')
  const debounceRef = useRef(null)
  useEffect(() => {
    clearTimeout(debounceRef.current)
    if (!query) { setSuggestions([]); return }
    debounceRef.current = setTimeout(async () => { setSuggestions(await searchStocks(query)); setShowSugg(true) }, 250)
  }, [query])
  function submit(sym) {
    const s = (sym || query).toUpperCase().trim()
    if (!s) return
    setQuery(s); setShowSugg(false); onAnalyse(s, exchange)
  }
  return (
    <div style={{width:'100%',maxWidth:680,margin:'0 auto'}}>
      <div style={{display:'flex',gap:8,marginBottom:12,justifyContent:'center'}}>
        {['NSE','BSE'].map(ex => (
          <button key={ex} onClick={()=>setExchange(ex)} style={{fontFamily:'var(--mono)',fontSize:'0.7rem',letterSpacing:2,padding:'5px 16px',border:'1px solid',borderColor:exchange===ex?'var(--accent)':'var(--border)',background:exchange===ex?'rgba(0,229,160,0.1)':'transparent',color:exchange===ex?'var(--accent)':'var(--muted)',cursor:'pointer',borderRadius:2}}>{ex}</button>
        ))}
      </div>
      <div style={{display:'flex',position:'relative'}}>
        <div style={{flex:1,position:'relative',display:'flex',alignItems:'center'}}>
          <span style={{position:'absolute',left:14,color:'var(--muted)',pointerEvents:'none',zIndex:1}}>⌕</span>
          <input value={query} onChange={e=>setQuery(e.target.value.toUpperCase())} onKeyDown={e=>e.key==='Enter'&&submit()} onFocus={()=>suggestions.length&&setShowSugg(true)} placeholder="Enter NSE symbol — RELIANCE, TCS, INFY..." disabled={loading}
            style={{width:'100%',background:'var(--card)',border:'1px solid var(--border)',borderRight:'none',outline:'none',padding:'15px 16px 15px 40px',fontFamily:'var(--mono)',fontSize:'0.9rem',color:'var(--text)',letterSpacing:1,borderRadius:'3px 0 0 3px'}} />
          {showSugg && suggestions.length > 0 && (
            <div style={{position:'absolute',top:'100%',left:0,right:0,background:'var(--card)',border:'1px solid var(--border)',borderTop:'none',borderRadius:'0 0 3px 3px',zIndex:100}}>
              {suggestions.map(s => (
                <div key={s.symbol} onMouseDown={()=>submit(s.symbol)} style={{display:'flex',alignItems:'center',gap:12,padding:'10px 16px',cursor:'pointer'}}
                  onMouseEnter={e=>e.currentTarget.style.background='#1a2535'} onMouseLeave={e=>e.currentTarget.style.background='transparent'}>
                  <span style={{fontFamily:'var(--mono)',fontWeight:700,fontSize:'0.8rem',color:'var(--accent)',minWidth:90}}>{s.symbol}</span>
                  <span style={{fontSize:'0.8rem',flex:1}}>{s.name}</span>
                  <span style={{fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)'}}>{s.sector}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        <button onClick={()=>submit()} disabled={loading||!query}
          style={{background:loading||!query?'var(--border)':'var(--accent)',color:loading||!query?'var(--muted)':'#000',border:'none',padding:'15px 28px',fontFamily:'var(--sans)',fontWeight:700,fontSize:'0.85rem',cursor:loading||!query?'not-allowed':'pointer',letterSpacing:1,textTransform:'uppercase',borderRadius:'0 3px 3px 0',whiteSpace:'nowrap'}}>
          {loading ? 'Analysing...' : 'Analyse →'}
        </button>
      </div>
      <div style={{display:'flex',alignItems:'center',gap:8,marginTop:12,flexWrap:'wrap',justifyContent:'center'}}>
        <span style={{fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)',letterSpacing:1}}>Quick:</span>
        {QUICK.map(s => <button key={s} onClick={()=>submit(s)} disabled={loading} style={{fontFamily:'var(--mono)',fontSize:'0.65rem',padding:'4px 10px',border:'1px solid var(--border)',background:'transparent',color:'var(--muted)',cursor:'pointer',borderRadius:2,letterSpacing:1}}>{s}</button>)}
      </div>
    </div>
  )
}
