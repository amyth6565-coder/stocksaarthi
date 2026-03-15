export default function VerdictCard({ ai, price }) {
  if (!ai) return null
  const colors = { BUY:'#00e5a0', HOLD:'#f5c518', AVOID:'#ff4757' }
  const c = colors[ai.verdict] || '#6b7f8e'
  const dayChange = price?.day_change_pct
  return (
    <div style={{background:'var(--card)',border:'1px solid var(--border)',borderRadius:4,padding:24,position:'relative',overflow:'hidden'}}>
      <div style={{position:'absolute',top:0,left:0,right:0,height:2,background:c}} />
      <div style={{fontFamily:'var(--mono)',fontSize:'0.62rem',color:'var(--muted)',letterSpacing:3,marginBottom:14}}>AI VERDICT</div>
      <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',marginBottom:16}}>
        <div style={{fontSize:'2.8rem',fontWeight:800,letterSpacing:-1,lineHeight:1,color:c}}>{ai.verdict}</div>
        <div style={{textAlign:'right'}}>
          <div style={{fontFamily:'var(--mono)',fontSize:'1.3rem',fontWeight:700}}>₹{price?.current?.toLocaleString('en-IN',{minimumFractionDigits:2})}</div>
          {dayChange!=null && <div style={{fontFamily:'var(--mono)',fontSize:'0.7rem',padding:'2px 8px',borderRadius:2,marginTop:4,display:'inline-block',color:dayChange>=0?'#00e5a0':'#ff4757',background:dayChange>=0?'rgba(0,229,160,0.1)':'rgba(255,71,87,0.1)'}}>{dayChange>=0?'+':''}{dayChange}%</div>}
        </div>
      </div>
      <div style={{display:'flex',justifyContent:'space-between',fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)',marginBottom:6}}><span>Confidence</span><span style={{color:c}}>{ai.confidence}%</span></div>
      <div style={{background:'var(--border)',borderRadius:2,height:3,overflow:'hidden',marginBottom:14}}><div style={{height:'100%',borderRadius:2,width:`${ai.confidence}%`,background:c}} /></div>
      <div style={{display:'inline-block',fontFamily:'var(--mono)',fontSize:'0.65rem',border:`1px solid ${c}40`,color:c,padding:'3px 10px',borderRadius:2,letterSpacing:1,marginBottom:14}}>⏱ {ai.time_horizon}</div>
      <p style={{fontFamily:'var(--mono)',fontSize:'0.78rem',lineHeight:1.7,color:'#b0c4d4',borderLeft:'2px solid var(--border)',paddingLeft:12,marginBottom:16}}>{ai.reasoning}</p>
      {ai.entry_strategy && <div style={{background:'rgba(0,229,160,0.05)',border:'1px solid rgba(0,229,160,0.15)',borderRadius:3,padding:'10px 14px',marginBottom:16}}>
        <div style={{fontFamily:'var(--mono)',fontSize:'0.58rem',color:'var(--accent)',letterSpacing:2,marginBottom:4}}>ENTRY STRATEGY</div>
        <div style={{fontFamily:'var(--mono)',fontSize:'0.75rem',color:'#b0c4d4',lineHeight:1.6}}>{ai.entry_strategy}</div>
      </div>}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
        <div>
          <div style={{fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)',letterSpacing:1,marginBottom:6}}><span style={{color:'#00e5a0'}}>✓</span> Positives</div>
          {(ai.key_positives||[]).map((p,i)=><div key={i} style={{fontFamily:'var(--mono)',fontSize:'0.7rem',color:'#8facc0',lineHeight:1.6,marginBottom:4,paddingLeft:10,borderLeft:'1px solid var(--border)'}}>{p}</div>)}
        </div>
        <div>
          <div style={{fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)',letterSpacing:1,marginBottom:6}}><span style={{color:'#ff4757'}}>⚠</span> Risks</div>
          {(ai.key_risks||[]).map((r,i)=><div key={i} style={{fontFamily:'var(--mono)',fontSize:'0.7rem',color:'#8facc0',lineHeight:1.6,marginBottom:4,paddingLeft:10,borderLeft:'1px solid var(--border)'}}>{r}</div>)}
        </div>
      </div>
    </div>
  )
}
