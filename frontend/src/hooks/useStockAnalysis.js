import { useState, useCallback } from 'react'
import { analyseStock } from '../utils/api'
export function useStockAnalysis() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const analyse = useCallback(async (sym, exchange = 'NSE') => {
    if (!sym) return
    setLoading(true); setError(null)
    try { setData(await analyseStock(sym, exchange)) }
    catch (e) { setError(e.message); setData(null) }
    finally { setLoading(false) }
  }, [])
  return { data, loading, error, analyse }
}
