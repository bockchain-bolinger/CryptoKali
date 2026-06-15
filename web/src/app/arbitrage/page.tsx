'use client';
import { useState, useEffect } from 'react';
import { scanArbitrage } from '@/lib/api';
import { Activity, RefreshCw, ArrowRightLeft, DollarSign, Target, Shuffle } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export default function ArbitragePage() {
  const [scanning, setScanning] = useState(false);
  const [opportunities, setOpportunities] = useState<any[]>([]);

  const handleScan = async () => {
    setScanning(true);
    try {
      const res = await scanArbitrage();
      setOpportunities(res);
    } catch (e) {
      console.error(e);
    }
    setScanning(false);
  };

  useEffect(() => {
    // Initial fetch
    handleScan();
  }, []);

  return (
    <div className="page animate-fade" style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: 'calc(100vh - var(--topbar-height))' }}>
      
      {/* Header Panel */}
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'linear-gradient(135deg, rgba(34, 211, 238, 0.05) 0%, rgba(99, 102, 241, 0.1) 100%)', border: '1px solid rgba(34, 211, 238, 0.2)', flexShrink: 0 }}>
        <div>
          <div className="section-title" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-cyan)' }}>
            <Shuffle size={20} /> Arbitrage Scanner & Smart Order Routing
          </div>
          <p style={{ margin: '8px 0 0 0', color: 'var(--text-secondary)', fontSize: '14px' }}>
            Live CCXT Engine scanning orderbooks across Binance, KuCoin, and Bitget for risk-free spreads.
          </p>
        </div>
        
        <button className="btn btn-primary" onClick={handleScan} disabled={scanning} style={{ padding: '12px 24px' }}>
          {scanning ? <Activity size={18} className="animate-spin" /> : <RefreshCw size={18} />}
          {scanning ? 'Scanning Market...' : 'Scan Now'}
        </button>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <div className="card" style={{ minHeight: '100%' }}>
          <div className="section-title" style={{ marginBottom: '16px' }}>Detected Opportunities</div>
          
          {opportunities.length === 0 && !scanning ? (
            <div className="text-muted" style={{ padding: '40px', textAlign: 'center' }}>No opportunities found. Run a scan.</div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '16px' }}>
              {opportunities.map((opp, idx) => (
                <div key={idx} style={{ background: 'var(--bg-secondary)', border: `1px solid ${opp.is_profitable ? 'rgba(34,197,94,0.3)' : 'var(--border)'}`, borderRadius: '12px', padding: '20px', position: 'relative', overflow: 'hidden' }}>
                  
                  {opp.is_profitable && (
                    <div style={{ position: 'absolute', top: 0, right: 0, background: 'var(--green)', color: '#000', fontSize: '10px', fontWeight: 'bold', padding: '4px 20px', transform: 'rotate(45deg) translate(15px, -15px)' }}>
                      PROFIT
                    </div>
                  )}

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ margin: 0, fontSize: '20px', color: 'var(--text-primary)' }}>{opp.symbol}</h3>
                    <div style={{ textAlign: 'right' }}>
                      <div className={opp.is_profitable ? 'text-positive' : 'text-negative'} style={{ fontSize: '22px', fontWeight: '900' }}>
                        {opp.is_profitable ? '+' : ''}{opp.net_spread_pct}%
                      </div>
                      <div className="text-muted" style={{ fontSize: '12px' }}>Net Spread</div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-primary)', padding: '12px', borderRadius: '8px', marginBottom: '16px' }}>
                    <div style={{ flex: 1 }}>
                      <Badge variant="blue" style={{ marginBottom: '4px', display: 'inline-block' }}>BUY @ {opp.buy_exchange.toUpperCase()}</Badge>
                      <div style={{ fontSize: '16px', fontWeight: 'bold' }}>${opp.buy_price.toLocaleString()}</div>
                    </div>
                    
                    <ArrowRightLeft size={20} className="text-muted" style={{ margin: '0 16px' }} />
                    
                    <div style={{ flex: 1, textAlign: 'right' }}>
                      <Badge variant="yellow" style={{ marginBottom: '4px', display: 'inline-block' }}>SELL @ {opp.sell_exchange.toUpperCase()}</Badge>
                      <div style={{ fontSize: '16px', fontWeight: 'bold' }}>${opp.sell_price.toLocaleString()}</div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }} disabled={!opp.is_profitable}>
                      <DollarSign size={16} /> Execute Route
                    </button>
                    <button className="btn" style={{ flex: 1, justifyContent: 'center', background: 'var(--bg-primary)' }}>
                      <Target size={16} /> Save to Paper
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
