import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import IPO from './pages/IPO'
import Chatbot from './components/Chatbot'

export default function App() {
  const [page, setPage] = useState('dashboard')

  return (
    <>
      <style>{`
        .nav-link {
          fontFamily: 'var(--mono)'; font-size: 0.75rem; letter-spacing: 1px;
          padding: 6px 14px; border-radius: 3px; cursor: pointer;
          border: 1px solid transparent; transition: all 0.15s;
          background: transparent; font-family: 'Space Mono', monospace;
          text-transform: uppercase;
        }
        .nav-link.active {
          color: var(--accent);
          border-color: rgba(0,229,160,0.3);
          background: rgba(0,229,160,0.08);
        }
        .nav-link:not(.active) {
          color: var(--muted);
        }
        .nav-link:not(.active):hover {
          color: var(--text);
          border-color: var(--border);
        }
      `}</style>

      {/* GLOBAL NAV */}
      <nav style={{
        borderBottom: '1px solid var(--border)',
        padding: '12px 0',
        position: 'sticky', top: 0,
        background: 'rgba(8,12,16,0.96)',
        backdropFilter: 'blur(12px)',
        zIndex: 100,
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Logo */}
          <div
            onClick={() => setPage('dashboard')}
            style={{ fontFamily: 'var(--sans)', fontWeight: 800, fontSize: '1.2rem', color: 'var(--accent)', letterSpacing: -0.5, cursor: 'pointer' }}
          >
            Stock<span style={{ color: 'var(--text)' }}>Saarthi</span>
            <span style={{ fontSize: '0.6rem', fontFamily: 'var(--mono)', color: 'var(--muted)', letterSpacing: 1, marginLeft: 8 }}>🇮🇳</span>
          </div>

          {/* Nav links */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <button
              className={`nav-link ${page === 'dashboard' ? 'active' : ''}`}
              onClick={() => setPage('dashboard')}
            >
              📊 Stocks
            </button>
            <button
              className={`nav-link ${page === 'ipo' ? 'active' : ''}`}
              onClick={() => setPage('ipo')}
            >
              🚀 IPO
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginLeft: 8 }}>
              <span style={{ display: 'inline-block', width: 6, height: 6, background: 'var(--accent)', borderRadius: '50%', animation: 'pulse 2s infinite' }} />
              <span style={{ fontFamily: 'var(--mono)', fontSize: '0.6rem', color: 'var(--muted)', letterSpacing: 1 }}>LIVE</span>
            </div>
          </div>
        </div>
      </nav>

      {/* PAGE CONTENT */}
      {page === 'dashboard' && <Dashboard hideNav />}
      {page === 'ipo' && <IPO />}

      {/* CHATBOT — always visible */}
      <Chatbot />
    </>
  )
}
