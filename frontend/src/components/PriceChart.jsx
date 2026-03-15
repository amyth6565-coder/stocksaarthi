import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
export default function PriceChart({ chartData, verdict }) {
  if (!chartData || chartData.length === 0) return null
  const color = verdict==='BUY'?'#00e5a0':verdict==='AVOID'?'#ff4757':'#f5c518'
  const minP = Math.min(...chartData.map(d=>d.low))
  const maxP = Math.max(...chartData.map(d=>d.high))
  const pad = (maxP-minP)*0.05
  const every = Math.max(1,Math.floor(chartData.length/6))
  return (
    <div style={{background:'var(--card)',border:'1px solid var(--border)',borderRadius:4,padding:'20px 20px 12px',position:'relative',overflow:'hidden'}}>
      <div style={{position:'absolute',top:0,left:0,right:0,height:2,background:color}} />
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:12}}>
        <div style={{fontFamily:'var(--mono)',fontSize:'0.62rem',color:'var(--muted)',letterSpacing:3}}>PRICE CHART — 90 DAYS</div>
        <div style={{fontFamily:'var(--mono)',fontSize:'0.72rem'}}>
          <span style={{color:'#ff4757'}}>Low ₹{minP.toLocaleString('en-IN',{maximumFractionDigits:0})}</span>
          <span style={{color:'var(--muted)',margin:'0 8px'}}>|</span>
          <span style={{color:'#00e5a0'}}>High ₹{maxP.toLocaleString('en-IN',{maximumFractionDigits:0})}</span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={chartData} margin={{top:8,right:0,left:0,bottom:0}}>
          <defs>
            <linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.3}/>
              <stop offset="100%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="date" tick={{fill:'#4a6070',fontSize:10,fontFamily:'Space Mono'}} tickLine={false} axisLine={false} tickFormatter={(d,i)=>i%every===0?d.slice(5):''} />
          <YAxis domain={[minP-pad,maxP+pad]} tick={{fill:'#4a6070',fontSize:10,fontFamily:'Space Mono'}} tickLine={false} axisLine={false} tickFormatter={v=>`₹${Math.round(v).toLocaleString('en-IN')}`} width={70}/>
          <Tooltip contentStyle={{background:'#111820',border:'1px solid #1e2d3d',borderRadius:3,fontFamily:'Space Mono',fontSize:11}} labelStyle={{color:'#6b7f8e'}} itemStyle={{color}} formatter={v=>[`₹${v.toLocaleString('en-IN')}`,'Close']}/>
          <Area type="monotone" dataKey="close" stroke={color} strokeWidth={2} fill="url(#pg)" dot={false} activeDot={{r:4,fill:color}}/>
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
