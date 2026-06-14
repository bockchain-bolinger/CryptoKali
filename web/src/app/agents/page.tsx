'use client';
import { useState, useEffect } from 'react';
import { fetchAgentStatus } from '@/lib/api';
import { ScoreBar } from '@/components/ui/ScoreBar';
import { Terminal, Activity, Play, Settings, RefreshCw } from 'lucide-react';

export default function AgentsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [logs, setLogs] = useState<string[]>([
    "[SYSTEM] AI Coordinator initialized",
    "[SYSTEM] Connecting to backend services...",
    "[SYSTEM] All services operational"
  ]);

  useEffect(() => {
    fetchAgentStatus().then(setAgents);

    const logMessages = [
      "[MarketAnalyst] Analyzing BTC/USDT order book... heavy resistance at 68k",
      "[SentimentAgent] Scanned 1200 tweets. Overall sentiment: 68 (Greed)",
      "[RiskAgent] Portfolio delta is neutral. Margin utilization at 12%",
      "[NewsAgent] Breaking: SEC delays ETF decision. Impact: Low",
      "[Coordinator] Evaluating Analyst recommendation for BTC LONG... Risk approved.",
      "[PortfolioAgent] Rebalancing suggested for Alts."
    ];

    const interval = setInterval(() => {
      const msg = logMessages[Math.floor(Math.random() * logMessages.length)];
      const time = new Date().toLocaleTimeString();
      setLogs(prev => [...prev.slice(-15), `[${time}] ${msg}`]);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page animate-fade">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>AI Agents Swarm</h1>
          <p>Monitor and control your autonomous trading agents</p>
        </div>
        <div>
          <button className="btn btn-secondary"><RefreshCw size={16} /> Restart All</button>
        </div>
      </div>

      <div className="grid-3" style={{ marginBottom: '24px' }}>
        {agents.map((agent) => (
          <div key={agent.id} className={`card ${agent.id === 'coordinator' ? 'card-glass' : ''}`} style={agent.id === 'coordinator' ? { borderColor: 'var(--accent-indigo)', boxShadow: 'var(--shadow-glow)' } : {}}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {agent.name}
                  <div className="live-dot" style={{ animationDuration: '3s' }}></div>
                </h3>
                <span className="text-positive" style={{ fontSize: '12px' }}>{agent.status}</span>
              </div>
              <button className="btn-icon"><Settings size={14} /></button>
            </div>
            
            <div style={{ marginBottom: '16px', background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: 'var(--radius-sm)', fontSize: '12px', minHeight: '40px', display: 'flex', alignItems: 'center' }}>
              <span className="text-secondary" style={{ marginRight: '8px' }}>Latest:</span>
              <span style={{ color: 'var(--text-primary)' }}>{agent.lastAction}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ width: '100px' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Confidence</div>
                <ScoreBar score={agent.confidence} showLabel={false} />
              </div>
              <button className="btn btn-sm btn-secondary"><Play size={12} /> Trigger</button>
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', height: '300px' }}>
        <div style={{ padding: '12px 16px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: 600 }}>
          <Terminal size={16} /> Swarm Event Log
        </div>
        <div style={{ padding: '16px', flex: 1, overflowY: 'auto', background: '#050505', fontFamily: 'monospace', fontSize: '12px', color: '#a3be8c', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {logs.map((log, i) => (
            <div key={i} className="animate-fade">
              {log.includes('[ERROR]') ? <span style={{ color: '#bf616a' }}>{log}</span> : 
               log.includes('[WARN]') ? <span style={{ color: '#ebcb8b' }}>{log}</span> : 
               log.includes('Coordinator') ? <span style={{ color: '#b48ead' }}>{log}</span> : log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
