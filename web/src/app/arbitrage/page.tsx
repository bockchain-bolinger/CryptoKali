'use client';
import { useState, useEffect } from 'react';
import { fetchArbitrageSpreads, rejectArbitrage, placePaperTrade } from '@/lib/api';
import { Badge } from '@/components/ui/Badge';
import { Check, X } from 'lucide-react';

export default function ArbitrageRadar() {
  const [data, setData] = useState<any>({ active: [], history: [] });
  const [autoTrade, setAutoTrade] = useState(false);

  useEffect(() => {
    async function load() {
      const res = await fetchArbitrageSpreads();
      setData(res);
    }
    load();
    const interval = setInterval(load, 5000); // 5s refresh
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (opp: any) => {
    // Optimistic UI update
    setData((prev: any) => ({
      ...prev,
      active: prev.active.map((o: any) => o.id === opp.id ? { ...o, status: 'executing' } : o)
    }));
    
    // Simulate placing 2 trades (buy on A, sell on B)
    await placePaperTrade({
      symbol: opp.symbol,
      side: 'BUY',
      entry_price: opp.buy_price,
      size: 0.1,
      strategy: 'Arbitrage_Leg1',
      stop: opp.buy_price * 0.95,
      tp1: opp.buy_price * 1.05
    });
    
    setTimeout(() => {
      setData((prev: any) => ({
        ...prev,
        active: prev.active.filter((o: any) => o.id !== opp.id)
      }));
    }, 1500);
  };

  const handleReject = async (oppId: string) => {
    setData((prev: any) => ({
      ...prev,
      active: prev.active.map((o: any) => o.id === oppId ? { ...o, status: 'radar_only' } : o)
    }));
    await rejectArbitrage(oppId);
  };

  return (
    <div className="page animate-fade">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Multi-Exchange Arbitrage</h1>
          <p>Live Spread Scanner: Binance, KuCoin, Bitget</p>
        </div>
        <div className="card-glass" style={{ padding: '12px 20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '14px', fontWeight: 'bold' }}>Auto-Trade Arbitrage</span>
          <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '40px', height: '20px' }}>
            <input type="checkbox" checked={autoTrade} onChange={(e) => setAutoTrade(e.target.checked)} style={{ opacity: 0, width: 0, height: 0 }} />
            <span style={{ 
              position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0, 
              backgroundColor: autoTrade ? 'var(--green)' : '#333', transition: '.4s', borderRadius: '34px'
            }}>
              <span style={{
                position: 'absolute', content: '""', height: '16px', width: '16px', left: '2px', bottom: '2px',
                backgroundColor: 'white', transition: '.4s', borderRadius: '50%',
                transform: autoTrade ? 'translateX(20px)' : 'translateX(0)'
              }}></span>
            </span>
          </label>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="section-title">Active Opportunities</div>
        
        {data.active.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            No profitable spreads detected at the moment. Scanning order books...
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Buy At</th>
                  <th>Sell At</th>
                  <th>Spread (%)</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {data.active.map((opp: any) => (
                  <tr key={opp.id} style={{ background: opp.status === 'pending_approval' ? 'rgba(99, 102, 241, 0.1)' : 'transparent' }}>
                    <td style={{ fontWeight: 'bold' }}>{opp.symbol}</td>
                    <td>
                      <Badge variant="blue">{opp.buy_exchange.toUpperCase()}</Badge>
                      <span style={{ marginLeft: '8px' }}>${opp.buy_price.toLocaleString()}</span>
                    </td>
                    <td>
                      <Badge variant="blue">{opp.sell_exchange.toUpperCase()}</Badge>
                      <span style={{ marginLeft: '8px' }}>${opp.sell_price.toLocaleString()}</span>
                    </td>
                    <td style={{ color: 'var(--green)', fontWeight: 'bold' }}>
                      +{opp.spread_pct.toFixed(2)}%
                    </td>
                    <td>
                      {opp.status === 'pending_approval' && <Badge variant="yellow">Awaiting Approval</Badge>}
                      {opp.status === 'executing' && <Badge variant="blue">Executing...</Badge>}
                      {opp.status === 'radar_only' && <span className="text-muted" style={{ fontSize: '13px' }}>Ignored (Radar)</span>}
                    </td>
                    <td>
                      {opp.status === 'pending_approval' && (
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button onClick={() => handleApprove(opp)} className="btn-primary" style={{ padding: '4px 12px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Check size={14} /> Approve
                          </button>
                          <button onClick={() => handleReject(opp.id)} className="btn-secondary" style={{ padding: '4px 12px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <X size={14} /> Reject
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
