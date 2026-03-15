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
  useEffect(() => { if (data && resultRef.current) resultRef.current.scrollIntoView({ behavior:'smooth', block:'start' }) }, [data])
  const verdict = data?.ai_verdict?.verdict
  return (
    <div style={{minHeight:'100vh',position:'relative',zIndex:1}}>
      <nav style={{borderBottom:'1px solid var(--border)',padding:'14px 0',position:'sticky',top:0,background:'rgba(8,12,16,0.96)',backdropFilter:'blur(12px)',zIndex:100}}>
        <div style={{maxWidth:1200,margin:'0 auto',padding:'0 24px',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div style={{fontFamily:'var(--sans)',fontWeight:800,fontSize:'1.25rem',color:'var(--accent)',letterSpacing:-0.5}}>Stock<span style={{color:'var(--text)'}}>Saarthi</span> <span style={{fontSize:'0.6rem',fontFamily:'var(--mono)',color:'var(--muted)',letterSpacing:1}}>🇮🇳 NSE/BSE</span></div>
          <div style={{display:'flex',alignItems:'center',gap:8}}>
            <span style={{display:'inline-block',width:6,height:6,background:'var(--accent)',borderRadius:'50%',animation:'pulse 2s infinite'}}/>
            <span style={{fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)',letterSpacing:1}}>LIVE DATA • AI POWERED • FREE STACK</span>
          </div>
        </div>
      </nav>

      <div style={{maxWidth:1200,margin:'0 auto',padding:'56px 24px 40px',textAlign:'center'}}>
        <div style={{display:'inline-block',fontFamily:'var(--mono)',fontSize:'0.68rem',color:'var(--accent)',background:'rgba(0,229,160,0.08)',border:'1px solid rgba(0,229,160,0.2)',padding:'4px 14px',borderRadius:2,letterSpacing:2,textTransform:'uppercase',marginBottom:18}}>Technical + Fundamental + AI Analysis</div>
        <h1 style={{fontSize:'clamp(2rem,5vw,3.2rem)',fontWeight:800,lineHeight:1.1,letterSpacing:-1,marginBottom:12}}>Should you <span style={{color:'var(--accent)'}}>buy</span> this<br/>Indian stock?</h1>
        <p style={{fontFamily:'var(--mono)',color:'var(--muted)',fontSize:'0.85rem',marginBottom:32}}>// Enter any NSE/BSE symbol — get instant AI-powered verdict</p>
        <SearchBar onAnalyse={analyse} loading={loading} />
      </div>

      <div style={{maxWidth:1200,margin:'0 auto',padding:'0 24px 40px'}}>
        {error && <div style={{background:'rgba(255,71,87,0.08)',border:'1px solid rgba(255,71,87,0.3)',borderRadius:4,padding:'14px 18px',fontFamily:'var(--mono)',fontSize:'0.8rem',color:'var(--danger)',marginBottom:24}}>⚠ {error}</div>}

        {loading && <div style={{display:'flex',alignItems:'center',gap:20,background:'var(--card)',border:'1px solid var(--border)',borderRadius:4,padding:'24px 28px',marginBottom:24}}>
          <div style={{width:32,height:32,flexShrink:0,border:'3px solid var(--border)',borderTop:'3px solid var(--accent)',borderRadius:'50%',animation:'spin 0.8s linear infinite'}}/>
          <div>
            <div style={{fontWeight:700,fontSize:'1rem',marginBottom:6}}>Analysing stock...</div>
            <div style={{fontFamily:'var(--mono)',fontSize:'0.7rem',color:'var(--muted)',lineHeight:1.6}}>Fetching price history → Calculating indicators → Scoring fundamentals → Getting AI verdict</div>
          </div>
        </div>}

        {data && !loading && <div ref={resultRef}>
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:20,paddingBottom:16,borderBottom:'1px solid var(--border)'}}>
            <div>
              <div style={{fontSize:'1.6rem',fontWeight:800,letterSpacing:-0.5,marginBottom:8}}>{data.company?.name}</div>
              <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
                {[{v:`${data.symbol}.${data.exchange}`,c:'var(--accent)',bg:'rgba(0,229,160,0.1)'},{v:data.company?.sector,c:'var(--muted)',bg:'var(--surface)'},{v:data.company?.industry,c:'var(--muted)',bg:'var(--surface)'}].map(({v,c,bg},i)=>v&&<span key={i} style={{fontFamily:'var(--mono)',fontSize:'0.7rem',color:c,background:bg,padding:'3px 10px',borderRadius:2}}>{v}</span>)}
              </div>
            </div>
            {verdict && <div style={{fontWeight:800,fontSize:'1.4rem',letterSpacing:1,color:{BUY:'#00e5a0',HOLD:'#f5c518',AVOID:'#ff4757'}[verdict],background:{BUY:'rgba(0,229,160,0.1)',HOLD:'rgba(245,197,24,0.1)',AVOID:'rgba(255,71,87,0.1)'}[verdict],border:`1px solid ${{BUY:'rgba(0,229,160,0.3)',HOLD:'rgba(245,197,24,0.3)',AVOID:'rgba(255,71,87,0.3)'}[verdict]}`,padding:'8px 20px',borderRadius:4}}>{verdict}</div>}
          </div>

          <div style={{display:'grid',gridTemplateColumns:'360px 1fr',gap:16,marginBottom:16}}>
            <VerdictCard ai={data.ai_verdict} price={data.price}/>
            <PriceChart chartData={data.technicals?.chart_data} verdict={verdict}/>
          </div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginBottom:16}}>
            <TechnicalPanel tech={data.technicals}/>
            <FundamentalsPanel fundamentals={data.fundamentals} fundScore={data.fundamental_score}/>
          </div>
          <div style={{fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)',textAlign:'center',padding:'12px',border:'1px solid var(--border)',borderRadius:3}}>⚠ For educational purposes only. Not financial advice. Always do your own research before investing.</div>
        </div>}

        {!data&&!loading&&!error&&<div style={{textAlign:'center',padding:'60px 24px'}}>
          <div style={{fontSize:'3rem',marginBottom:16}}>📊</div>
          <div style={{fontWeight:700,fontSize:'1.1rem',marginBottom:8}}>Enter a stock symbol above</div>
          <div style={{fontFamily:'var(--mono)',color:'var(--muted)',fontSize:'0.8rem'}}>Try RELIANCE, TCS, HDFCBANK, INFY or any NSE symbol</div>
        </div>}
      </div>

      <footer style={{borderTop:'1px solid var(--border)',padding:'20px 0',textAlign:'center'}}>
        <p style={{fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)'}}>StockSaarthi · Powered by yfinance + Groq (Llama 3.3 70B) + FastAPI · For educational use only</p>
      </footer>
    </div>
  )
}
