const SC = {BULLISH:'#00e5a0','STRONG BULLISH':'#00e5a0','BULLISH CROSSOVER':'#00e5a0',BEARISH:'#ff4757','STRONG BEARISH':'#ff4757','BEARISH CROSSOVER':'#ff4757',OVERBOUGHT:'#f5c518',OVERSOLD:'#5b8dee',NEUTRAL:'#6b7f8e','N/A':'#6b7f8e','STRONG UPTREND':'#00e5a0',UPTREND:'#00e5a0',DOWNTREND:'#ff4757',MIXED:'#f5c518','ABOVE MID — BULLISH':'#00e5a0','BELOW MID — BEARISH':'#ff4757','VERY HIGH VOLUME':'#00e5a0','HIGH VOLUME':'#00e5a0','LOW VOLUME':'#ff4757',AVERAGE:'#6b7f8e'}
function Row({name,value,signal}){const c=SC[signal]||'#6b7f8e';return(
  <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'8px 0',borderBottom:'1px solid var(--border)',gap:8}}>
    <span style={{fontFamily:'var(--mono)',fontSize:'0.72rem',color:'var(--muted)',flex:1}}>{name}</span>
    <span style={{fontFamily:'var(--mono)',fontSize:'0.72rem',minWidth:80,textAlign:'right'}}>{value}</span>
    <span style={{fontFamily:'var(--mono)',fontSize:'0.6rem',padding:'2px 7px',borderRadius:2,letterSpacing:0.5,border:'1px solid',color:c,background:`${c}18`,borderColor:`${c}30`,whiteSpace:'nowrap',minWidth:90,textAlign:'center'}}>{signal}</span>
  </div>
)}
export default function TechnicalPanel({tech}){
  if(!tech)return null
  const {rsi,macd,ema,bollinger,stochastic,volume,technical_score,technical_summary}=tech
  const sc=technical_score>=7?'#00e5a0':technical_score>=5?'#f5c518':'#ff4757'
  return(
    <div style={{background:'var(--card)',border:'1px solid var(--border)',borderRadius:4,padding:20,position:'relative',overflow:'hidden'}}>
      <div style={{position:'absolute',top:0,left:0,right:0,height:2,background:'#ff6b35'}}/>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:4}}>
        <div style={{fontFamily:'var(--mono)',fontSize:'0.62rem',color:'var(--muted)',letterSpacing:3}}>TECHNICAL INDICATORS</div>
        <div style={{display:'flex',alignItems:'baseline',gap:2}}><span style={{fontFamily:'var(--mono)',fontWeight:700,fontSize:'1.4rem',color:sc}}>{technical_score}</span><span style={{fontFamily:'var(--mono)',fontSize:'0.7rem',color:'var(--muted)'}}>/10</span></div>
      </div>
      <div style={{fontFamily:'var(--mono)',fontSize:'0.72rem',color:sc,marginBottom:14}}>{technical_summary}</div>
      {rsi?.value!=null&&<Row name={`RSI (14) — ${rsi.value}`} value="" signal={rsi.signal}/>}
      {macd?.value!=null&&<Row name="MACD" value={`${macd.value} / ${macd.signal_line}`} signal={macd.signal}/>}
      {ema?.ema20!=null&&<Row name="EMA 20/50/200" value={`${ema.ema20} / ${ema.ema50??'-'} / ${ema.ema200??'-'}`} signal={ema.signal}/>}
      {bollinger?.upper!=null&&<Row name="Bollinger Bands" value={`${bollinger.lower}—${bollinger.upper}`} signal={bollinger.signal}/>}
      {stochastic?.k!=null&&<Row name="Stochastic %K/%D" value={`${stochastic.k}/${stochastic.d}`} signal={stochastic.signal}/>}
      {volume?.ratio!=null&&<Row name="Volume vs 20D Avg" value={`${volume.ratio}x`} signal={volume.signal}/>}
      {tech.high_52w&&<div style={{marginTop:14}}>
        <div style={{fontFamily:'var(--mono)',fontSize:'0.58rem',color:'var(--muted)',letterSpacing:2,marginBottom:8}}>52-WEEK RANGE</div>
        <div style={{display:'flex',alignItems:'center',gap:10}}>
          <span style={{fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)',whiteSpace:'nowrap'}}>₹{tech.low_52w?.toLocaleString('en-IN')}</span>
          <div style={{flex:1,height:4,background:'var(--border)',borderRadius:2,position:'relative'}}>
            <div style={{position:'absolute',top:'50%',transform:'translate(-50%,-50%)',left:`${Math.max(0,Math.min(100,((tech.close-tech.low_52w)/(tech.high_52w-tech.low_52w))*100))}%`,width:10,height:10,borderRadius:'50%',background:'#00e5a0',border:'2px solid var(--bg)'}}/>
          </div>
          <span style={{fontFamily:'var(--mono)',fontSize:'0.65rem',color:'var(--muted)',whiteSpace:'nowrap'}}>₹{tech.high_52w?.toLocaleString('en-IN')}</span>
        </div>
      </div>}
    </div>
  )
}
