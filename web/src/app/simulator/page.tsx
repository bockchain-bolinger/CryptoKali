'use client';
import { useState } from 'react';
import { simulateMacroScenario } from '@/lib/api';
import { Activity, Beaker, TrendingUp, TrendingDown, RefreshCw, BarChart2, DollarSign } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export default function SimulatorPage() {
  const [dxyChange, setDxyChange] = useState<number>(0);
  const [rateChange, setRateChange] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const res = await simulateMacroScenario(dxyChange, rateChange);
      setResult(res);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const getSentimentColor = (sentiment: str) => {
    if (sentiment.includes('Bullish')) return 'text-positive';
    if (sentiment.includes('Bearish')) return 'text-negative';
    return 'text-muted';
  };

  return (
    <div className="page animate-fade" style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: 'calc(100vh - var(--topbar-height))' }}>
      
      {/* Header */}
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%)', border: '1px solid rgba(236, 72, 153, 0.2)', flexShrink: 0 }}>
        <div>
          <div className="section-title" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px', color: '#f472b6' }}>
            <Beaker size={22} /> "What-If" Macro Simulator
          </div>
          <p style={{ margin: '8px 0 0 0', color: 'var(--text-secondary)', fontSize: '14px' }}>
            Adjust the FED Interest Rates and DXY index to simulate the AI's projected impact on the crypto ecosystem.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '24px', flex: 1, overflowY: 'auto' }}>
        
        {/* Controls Panel */}
        <div className="card" style={{ flex: '0 0 350px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="section-title">Scenario Variables</div>
          
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '14px', fontWeight: 'bold' }}>US Dollar Index (DXY) Change</label>
              <span className={dxyChange > 0 ? 'text-positive' : dxyChange < 0 ? 'text-negative' : ''} style={{ fontWeight: 'bold' }}>
                {dxyChange > 0 ? '+' : ''}{dxyChange}%
              </span>
            </div>
            <input 
              type="range" 
              min="-10" max="10" step="0.5" 
              value={dxyChange} 
              onChange={(e) => setDxyChange(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer' }}
            />
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px' }}>
              A weaker dollar (negative) historically drives crypto prices up.
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border)', margin: '8px 0' }}></div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '14px', fontWeight: 'bold' }}>FED Interest Rate Change</label>
              <span className={rateChange > 0 ? 'text-positive' : rateChange < 0 ? 'text-negative' : ''} style={{ fontWeight: 'bold' }}>
                {rateChange > 0 ? '+' : ''}{rateChange}%
              </span>
            </div>
            <input 
              type="range" 
              min="-3" max="3" step="0.25" 
              value={rateChange} 
              onChange={(e) => setRateChange(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer' }}
            />
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px' }}>
              Rate cuts (negative) inject liquidity into high-risk assets like Crypto.
            </div>
          </div>

          <button className="btn btn-primary" style={{ marginTop: 'auto', justifyContent: 'center', padding: '12px' }} onClick={handleSimulate} disabled={loading}>
            {loading ? <Activity size={18} className="animate-spin" /> : <RefreshCw size={18} />}
            Run AI Simulation
          </button>
        </div>

        {/* Results Panel */}
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div className="section-title" style={{ marginBottom: '24px' }}>Simulation Results</div>
          
          {!result && !loading && (
            <div className="text-muted" style={{ margin: 'auto', textAlign: 'center', padding: '40px' }}>
              <Beaker size={48} style={{ margin: '0 auto 16px auto', opacity: 0.5 }} />
              <div>Adjust the sliders and click "Run AI Simulation"</div>
            </div>
          )}

          {loading && (
            <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--accent-indigo)' }}>
              <Activity size={48} className="animate-spin" style={{ margin: '0 auto 16px auto' }} />
              <div>MacroAgent is calculating projections...</div>
            </div>
          )}

          {result && !loading && (
            <div className="animate-fade" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1, background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px', padding: '20px', textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>BTC Projected Impact</div>
                  <div className={result.projections.btc_impact_pct >= 0 ? 'text-positive' : 'text-negative'} style={{ fontSize: '32px', fontWeight: 'bold' }}>
                    {result.projections.btc_impact_pct >= 0 ? '+' : ''}{result.projections.btc_impact_pct}%
                  </div>
                  <div style={{ fontSize: '14px', marginTop: '8px' }}>Target: ${result.projections.projected_btc.toLocaleString()}</div>
                </div>
                
                <div style={{ flex: 1, background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px', padding: '20px', textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>ETH Projected Impact</div>
                  <div className={result.projections.eth_impact_pct >= 0 ? 'text-positive' : 'text-negative'} style={{ fontSize: '32px', fontWeight: 'bold' }}>
                    {result.projections.eth_impact_pct >= 0 ? '+' : ''}{result.projections.eth_impact_pct}%
                  </div>
                  <div style={{ fontSize: '14px', marginTop: '8px' }}>Target: ${result.projections.projected_eth.toLocaleString()}</div>
                </div>

                <div style={{ flex: 1, background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px', padding: '20px', textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>Overall Sentiment</div>
                  <div className={getSentimentColor(result.projections.sentiment)} style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '4px' }}>
                    {result.projections.sentiment.toUpperCase()}
                  </div>
                  <div style={{ fontSize: '14px', marginTop: '12px', color: 'var(--text-secondary)' }}>DeFi TVL: {result.projections.tvl_impact_pct >= 0 ? '+' : ''}{result.projections.tvl_impact_pct}%</div>
                </div>
              </div>

              <div style={{ background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.2)', borderRadius: '12px', padding: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: 'var(--accent-indigo)', fontWeight: 'bold' }}>
                  <BarChart2 size={18} /> AI Macro Flash Report
                </div>
                <p style={{ margin: 0, fontSize: '15px', lineHeight: '1.6', color: 'var(--text-primary)' }}>
                  {result.report}
                </p>
              </div>

            </div>
          )}

        </div>
      </div>
    </div>
  );
}
