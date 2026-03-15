const BASE = '/api'
export async function analyseStock(symbol, exchange = 'NSE') {
  const res = await fetch(`${BASE}/analyse/${symbol}?exchange=${exchange}`)
  if (!res.ok) { const e = await res.json().catch(()=>({})); throw new Error(e.detail || `Failed to analyse ${symbol}`) }
  return res.json()
}
export async function searchStocks(query) {
  if (!query) return []
  const res = await fetch(`${BASE}/search?q=${encodeURIComponent(query)}`)
  if (!res.ok) return []
  return (await res.json()).results || []
}
export function formatCurrency(val) {
  if (val == null) return 'N/A'
  if (val >= 1e12) return `₹${(val/1e12).toFixed(2)}T`
  if (val >= 1e9) return `₹${(val/1e9).toFixed(2)}B`
  if (val >= 1e7) return `₹${(val/1e7).toFixed(2)}Cr`
  return `₹${val?.toLocaleString('en-IN') ?? 'N/A'}`
}
