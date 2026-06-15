'use client';
import { useState, useEffect } from 'react';
import { fetchSignals } from '@/lib/api';
import { Badge } from '@/components/ui/Badge';
import { ScoreBar } from '@/components/ui/ScoreBar';
import { Modal } from '@/components/ui/Modal';
import { Download, RefreshCw, Filter, Crosshair, Play } from 'lucide-react';

export default function SignalsPage() {
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const [minScore, setMinScore] = useState(60);

  const loadSignals = async () => {
    setLoading(true);
    const data = await fetchSignals();
    setSignals(data.filter(s => s.score >= minScore));
    setLoading(false);
  };

  useEffect(() => {
    loadSignals();
  }, [minScore]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(loadSignals, 30000);
    return () => clearInterval(interval);
  }, [autoRefresh, minScore]);

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(signals, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'apex_ai_signals.json';
    a.click();
  };

  return (
    <div className="page animate-fade">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Trading Signals</h1>
          <p>AI-generated opportunities across multiple venues</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-secondary" onClick={exportJSON}>
            <Download size={16} /> Export JSON
          </button>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '24px', padding: '16px' }}>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} className="text-muted" />
            <span style={{ fontSize: '13px', fontWeight: 500 }}>Venue:</span>
            <select className="input" style={{ width: 'auto', padding: '6px 12px' }}>
              <option>All Venues</option>
              <option>Binance</option>
              <option>Bybit</option>
              <option>KuCoin</option>
            </select>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
            <span style={{ fontSize: '13px', fontWeight: 500 }}>Min Score ({minScore}):</span>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={minScore} 
              onChange={(e) => setMinScore(parseInt(e.target.value))}
              style={{ flex: 1, maxWidth: '200px' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: 500 }}>Timeframe:</span>
            <select className="input" style={{ width: 'auto', padding: '6px 12px' }}>
              <option>All</option>
              <option>15m</option>
              <option>1h</option>
              <option>4h</option>
              <option>1D</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderLeft: '1px solid var(--border)', paddingLeft: '20px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px' }}>
              <input 
                type="checkbox" 
                checked={autoRefresh} 
                onChange={(e) => setAutoRefresh(e.target.checked)} 
              />
              Auto-Refresh (30s)
            </label>
            <button className="btn-icon" onClick={loadSignals} disabled={loading}>
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="table-wrapper">
          <table style={{ minWidth: '800px' }}>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Venue</th>
                <th>Strategy</th>
                <th>Score</th>
                <th>Entry</th>
                <th>Stop</th>
                <th>TP1</th>
                <th>TP2</th>
                <th>Time</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((sig) => (
                <tr key={sig.id} onClick={() => setSelectedSignal(sig)} style={{ cursor: 'pointer' }}>
                  <td style={{ fontWeight: 600 }}>{sig.symbol}</td>
                  <td>{sig.venue}</td>
                  <td className="text-muted">{sig.strategy}</td>
                  <td style={{ minWidth: '120px' }}><ScoreBar score={sig.score} /></td>
                  <td>${sig.entry}</td>
                  <td className="text-negative">${sig.stop}</td>
                  <td className="text-positive">${sig.tp1}</td>
                  <td className="text-positive">${sig.tp2}</td>
                  <td className="text-muted">{sig.time}</td>
                  <td>
                    <Badge variant={sig.action === 'LONG' ? 'green' : 'red'}>{sig.action}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {signals.length === 0 && !loading && (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
              No signals found matching criteria
            </div>
          )}
        </div>
      </div>

      <Modal open={!!selectedSignal} onClose={() => setSelectedSignal(null)} title="Signal Details">
        {selectedSignal && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <div>
                <h3 style={{ fontSize: '24px', fontWeight: 700 }}>{selectedSignal.symbol}</h3>
                <span className="text-muted">{selectedSignal.venue} • {selectedSignal.strategy}</span>
              </div>
              <div>
                <Badge variant={selectedSignal.action === 'LONG' ? 'green' : 'red'}><span style={{ fontSize: '16px' }}>{selectedSignal.action}</span></Badge>
              </div>
            </div>

            <div className="grid-2" style={{ marginBottom: '24px' }}>
              <div className="card-glass" style={{ padding: '16px' }}>
                <div className="text-muted" style={{ marginBottom: '4px' }}>Entry Range</div>
                <div style={{ fontSize: '18px', fontWeight: 600 }}>${selectedSignal.entry}</div>
              </div>
              <div className="card-glass" style={{ padding: '16px' }}>
                <div className="text-muted" style={{ marginBottom: '4px' }}>Stop Loss</div>
                <div className="text-negative" style={{ fontSize: '18px', fontWeight: 600 }}>${selectedSignal.stop}</div>
              </div>
              <div className="card-glass" style={{ padding: '16px' }}>
                <div className="text-muted" style={{ marginBottom: '4px' }}>Take Profit 1</div>
                <div className="text-positive" style={{ fontSize: '18px', fontWeight: 600 }}>${selectedSignal.tp1}</div>
              </div>
              <div className="card-glass" style={{ padding: '16px' }}>
                <div className="text-muted" style={{ marginBottom: '4px' }}>Take Profit 2</div>
                <div className="text-positive" style={{ fontSize: '18px', fontWeight: 600 }}>${selectedSignal.tp2}</div>
              </div>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <div className="text-muted" style={{ marginBottom: '8px' }}>AI Confidence Score</div>
              <ScoreBar score={selectedSignal.score} />
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedSignal(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={() => {
                alert('Paper trade executed!');
                setSelectedSignal(null);
              }}>
                <Play size={16} /> Paper Trade
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
