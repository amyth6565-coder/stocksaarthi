import { useState, useRef, useEffect } from 'react'

const SUGGESTIONS = [
  "Should I buy RELIANCE?",
  "Compare TCS vs INFY",
  "What is RSI?",
  "Analyse HDFCBANK",
]

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom: 12 }}>
      {!isUser && (
        <div style={{ width: 26, height: 26, borderRadius: '50%', background: 'rgba(0,229,160,0.15)', border: '1px solid rgba(0,229,160,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', marginRight: 7, flexShrink: 0, marginTop: 2 }}>🤖</div>
      )}
      <div style={{
        maxWidth: '82%',
        background: isUser ? 'rgba(0,229,160,0.12)' : 'var(--surface)',
        border: `1px solid ${isUser ? 'rgba(0,229,160,0.25)' : 'var(--border)'}`,
        borderRadius: isUser ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
        padding: '9px 12px',
      }}>
        {msg.tool_used && (
          <div style={{ fontFamily: 'var(--mono)', fontSize: '0.55rem', color: 'var(--accent)', letterSpacing: 1, marginBottom: 5 }}>
            ⚡ {msg.tool_used.toUpperCase().replace(/_/g, ' ')}
          </div>
        )}
        <div style={{ fontFamily: 'var(--mono)', fontSize: '0.75rem', lineHeight: 1.7, color: isUser ? 'var(--accent)' : '#c8dce8', whiteSpace: 'pre-wrap' }}>
          {msg.content}
        </div>
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
      <div style={{ width: 26, height: 26, borderRadius: '50%', background: 'rgba(0,229,160,0.15)', border: '1px solid rgba(0,229,160,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem' }}>🤖</div>
      <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '12px 12px 12px 2px', padding: '10px 14px', display: 'flex', gap: 4 }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--accent)', animation: 'bounce 1.2s infinite', animationDelay: `${i * 0.2}s` }} />
        ))}
      </div>
    </div>
  )
}

export default function Chatbot() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Namaste! 🇮🇳 I'm StockSaarthi AI.\n\nAsk me anything about Indian stocks — analysis, comparisons, technical indicators.\n\nTry: \"Should I buy RELIANCE?\"" }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  // Responsive chat window size
  const isMobile = typeof window !== 'undefined' && window.innerWidth <= 480

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])
  useEffect(() => { if (open) setTimeout(() => inputRef.current?.focus(), 100) }, [open])

  async function send(text) {
    const msg = text || input.trim()
    if (!msg || loading) return
    setInput('')
    const userMsg = { role: 'user', content: msg }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setLoading(true)
    try {
      const history = newMessages.slice(1).map(m => ({ role: m.role, content: m.content }))
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: history.slice(-6) })
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply, tool_used: data.tool_used }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: '⚠️ Connection error. Make sure backend is running.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <style>{`
        @keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-5px)} }
        @keyframes slideUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
        .chat-window {
          position: fixed; bottom: 86px; right: 16px; z-index: 999;
          width: 360px; height: 540px;
          background: var(--card); border: 1px solid var(--border);
          border-radius: 14px; display: flex; flex-direction: column;
          box-shadow: 0 8px 48px rgba(0,0,0,0.6);
          animation: slideUp 0.2s ease;
        }
        @media (max-width: 480px) {
          .chat-window {
            width: calc(100vw - 16px) !important;
            right: 8px !important;
            bottom: 80px !important;
            height: 70vh !important;
          }
        }
      `}</style>

      {/* Floating button */}
      <button onClick={() => setOpen(!open)} style={{
        position: 'fixed', bottom: 20, right: 16, zIndex: 1000,
        width: 52, height: 52, borderRadius: '50%',
        background: open ? 'var(--danger)' : 'var(--accent)',
        border: 'none', cursor: 'pointer', fontSize: '1.3rem',
        boxShadow: `0 4px 20px ${open ? 'rgba(255,71,87,0.4)' : 'rgba(0,229,160,0.4)'}`,
        transition: 'all 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {open ? '✕' : '💬'}
      </button>

      {open && (
        <div className="chat-window">
          {/* Header */}
          <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 9, flexShrink: 0 }}>
            <div style={{ width: 30, height: 30, borderRadius: '50%', background: 'rgba(0,229,160,0.15)', border: '1px solid rgba(0,229,160,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🤖</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: '0.88rem' }}>StockSaarthi AI</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: '0.58rem', color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--accent)', display: 'inline-block', animation: 'pulse 2s infinite' }} />
                LIVE NSE/BSE DATA
              </div>
            </div>
            <button onClick={() => setMessages([messages[0]])} style={{ background: 'none', border: '1px solid var(--border)', color: 'var(--muted)', cursor: 'pointer', borderRadius: 4, padding: '3px 8px', fontFamily: 'var(--mono)', fontSize: '0.58rem' }}>CLEAR</button>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '12px 10px' }}>
            {messages.map((m, i) => <Message key={i} msg={m} />)}
            {loading && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>

          {/* Suggestions */}
          {messages.length <= 1 && (
            <div style={{ padding: '0 10px 8px', display: 'flex', gap: 5, flexWrap: 'wrap' }}>
              {SUGGESTIONS.map(s => (
                <button key={s} onClick={() => send(s)}
                  style={{ fontFamily: 'var(--mono)', fontSize: '0.58rem', padding: '4px 8px', background: 'transparent', border: '1px solid var(--border)', color: 'var(--muted)', cursor: 'pointer', borderRadius: 4 }}
                  onMouseEnter={e => { e.target.style.borderColor = 'var(--accent)'; e.target.style.color = 'var(--accent)' }}
                  onMouseLeave={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.color = 'var(--muted)' }}>
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div style={{ padding: '10px', borderTop: '1px solid var(--border)', display: 'flex', gap: 7, flexShrink: 0 }}>
            <input
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && send()}
              placeholder="Ask about any NSE stock..."
              disabled={loading}
              style={{ flex: 1, background: 'var(--surface)', border: '1px solid var(--border)', outline: 'none', padding: '9px 11px', fontFamily: 'var(--mono)', fontSize: '0.75rem', color: 'var(--text)', borderRadius: 6 }}
            />
            <button onClick={() => send()} disabled={loading || !input.trim()}
              style={{ background: loading || !input.trim() ? 'var(--border)' : 'var(--accent)', color: loading || !input.trim() ? 'var(--muted)' : '#000', border: 'none', borderRadius: 6, padding: '9px 13px', cursor: loading || !input.trim() ? 'not-allowed' : 'pointer', fontWeight: 700, fontSize: '1rem' }}>
              ↑
            </button>
          </div>
        </div>
      )}
    </>
  )
}
