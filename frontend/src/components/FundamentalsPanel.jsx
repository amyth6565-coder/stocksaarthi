export default function FundamentalsPanel({fundamentals,fundScore}){
  if(!fundScore||!fundamentals)return null
  const {fundamental_score,fundamental_summary,metrics}=fundScore
  const sc=fundamental_score>=7?'#00e5a0':fundamental_score>=5?'#f5c518':'#ff4757'
  const gc={'A+':'#00e5a0','A':'#00e5a0','B+':'#5b8dee','B':'#5b8dee','C+':'#f5c518','C':'#f5c518','D':'#ff4757'}
  const m=metrics||{}
  return(
    <div style={{background:'var(--card)',border:'1px solid var(--border)',borderRadius:4,padding:20,position:'relative',overflow:'hidden'}}>
      <div style={{position:'absolute',top:0,left:0,right:0,height:2,background:'#f5c518'}}/>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:4}}>
        <div style={{fontFamily:'var(--mono)',fontSize:'0.62rem',color:'var(--muted)',letterSpacing:3}}>FUNDAMENTALS</div>
        <div style={{display:'flex',alignItems:'baseline',gap:2}}><span style={{fontFamily:'var(--mono)',fontWeight:700,fontSize:'1.4rem',color:sc}}>{fundamental_score}</span><span style={{fontFamily:'var(--mono)',fontSize:'0.7rem',color:'var(--muted)'}}>/10</span></div>
      </div>
      <div style={{fontFamily:'var(--mono)',fontSize:'0.72rem',color:sc,marginBottom:12}}>{fundamental_summary}</div>
      <div style={{display:'flex',gap:16,marginBottom:14,paddingBottom:12,borderBottom:'1px solid var(--border)',flexWrap:'wrap'}}>
        {[['Sector',fundamentals.sector],['Market Cap',fundamentals.market_cap?`₹${(fundamentals.market_cap/1e7).toFixed(0)}Cr`:'N/A'],['Target',fundamentals.target_mean_price?`₹${fundamentals.target_mean_price}`:'N/A']].map(([l,v])=>(
          <span key={l} style={{display:'flex',flexDirection:'column',gap:2}}>
            <span style={{fontFamily:'var(--mono)',fontSize:'0.58rem',color:'var(--muted)',letterSpacing:1}}>{l}</span>
            <span style={{fontFamily:'var(--mono)',fontSize:'0.75rem',fontWeight:700}}>{v||'N/A'}</span>
          </span>
        ))}
      </div>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:1,background:'var(--border)'}}>
        {Object.entries(m).map(([key,data])=>{
          const c=gc[data.grade]||'#6b7f8e'
          return(
            <div key={key} style={{background:'var(--card)',padding:'10px 12px'}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:3}}>
                <span style={{fontFamily:'var(--mono)',fontSize:'0.6rem',color:'var(--muted)',letterSpacing:1}}>{key.replace(/_/g,' ').toUpperCase()}</span>
                <span style={{fontFamily:'var(--mono)',fontSize:'0.6rem',fontWeight:700,padding:'1px 5px',borderRadius:2,color:c,background:`${c}15`}}>{data.grade}</span>
              </div>
              <div style={{fontFamily:'var(--mono)',fontWeight:700,fontSize:'1rem'}}>{data.value}</div>
              <div style={{fontFamily:'var(--mono)',fontSize:'0.6rem',color:'var(--muted)',marginTop:2}}>{data.note}</div>
            </div>
          )
        })}
      </div>
      {fundamentals.analyst_recommendation&&<div style={{marginTop:12,display:'flex',alignItems:'center',justifyContent:'space-between',padding:'8px 12px',background:'rgba(91,141,238,0.08)',border:'1px solid rgba(91,141,238,0.2)',borderRadius:3}}>
        <span style={{fontFamily:'var(--mono)',fontSize:'0.58rem',color:'var(--muted)',letterSpacing:2}}>ANALYST CONSENSUS</span>
        <span style={{fontFamily:'var(--mono)',fontWeight:700,fontSize:'0.8rem',color:'#5b8dee'}}>{fundamentals.analyst_recommendation?.toUpperCase()} {fundamentals.number_of_analysts&&<span style={{fontWeight:400,color:'var(--muted)'}}>({fundamentals.number_of_analysts} analysts)</span>}</span>
      </div>}
    </div>
  )
}
