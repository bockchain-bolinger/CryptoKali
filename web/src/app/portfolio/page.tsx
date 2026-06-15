'use client';
import { useState, useEffect } from 'react';
import { Activity, Briefcase, RefreshCw, AlertTriangle, ShieldCheck, PieChart } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { fetchRiskStatus, optimizePortfolio, closePaperTrade } from '@/lib/api';

export default function PortfolioPage() {
  const [riskStatus, setRiskStatus] = useState<any>(null);
  const [optimizing, setOptimizing] = useState(false);
  const [optimalAlloc, setOptimalAlloc] = useState<any>(null);

  useEffect(() => {
    fetchRiskStatus().then(setRiskStatus);
  }, []);

  const handleOptimize = async () => {
    setOptimizing(true);
    try {
      const res = await optimizePortfolio(["BTC/USDT", "ETH/USDT", "BNB/USDT"]);
      if (res.status === "success" || res.weights) {
        setOptimalAlloc(res);
      }
    } catch (e) {
      console.error(e);
    }
    setOptimizing(false);
  };

  return (
    <div className="page animate-fade" style={{ display: 'flex', gap: '24px', height: 'calc(100vh - var(--topbar-height))' }}>
      {/* Left Column: Summary & Sentinel */}
      <div style={{ width: '320px', display: 'flex', flexDirection: 'column', gap: '24px', flexShrink: 0 }}>
        
        {/* Total Value Card */}
        <div className="card" style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(34, 211, 238, 0.05) 100%)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
          <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-indigo)' }}>
            <Briefcase size={18} /> Portfolio Value
          </div>
          <div style={{ fontSize: '36px', fontWeight: '900', color: 'var(--text-primary)', margin: '8px 0' }}>
            ${riskStatus?.total_capital_tracked ? riskStatus.total_capital_tracked.toLocaleString() : '10,000.00'}
          </div>
          <div style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Unrealized P&L</div>
              <div className="text-positive" style={{ fontWeight: 'bold' }}>+$450.20</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Realized P&L</div>
              <div className="text-positive" style={{ fontWeight: 'bold' }}>+$1,240.50</div>
            </div>
          </div>
        </div>

        {/* Sentinel Risk Status */}
        <div className="card">
          <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {riskStatus?.status === 'DANGER' ? <AlertTriangle size={18} className="text-negative" /> : <ShieldCheck size={18} className="text-positive" />}
            Apex Sentinel Status
          </div>
          
          {riskStatus ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>System State</span>
                <Badge variant={riskStatus.status === 'SAFE' ? 'green' : (riskStatus.status === 'WARNING' ? 'yellow' : 'red')}>
                  {riskStatus.status}
                </Badge>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Max Risk / Trade</span>
                <span style={{ fontWeight: 'bold' }}>{riskStatus.max_risk_per_trade_pct}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Max Daily Drawdown</span>
                <span style={{ fontWeight: 'bold' }}>{riskStatus.max_daily_drawdown_pct}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Open Positions</span>
                <span style={{ fontWeight: 'bold' }}>{riskStatus.current_open_positions} / {riskStatus.max_open_positions}</span>
              </div>
            </div>
          ) : (
            <div className="text-muted" style={{ textAlign: 'center', padding: '20px 0' }}>Loading Risk Status...</div>
          )}
        </div>

        {/* Action Buttons */}
        <button className="btn btn-primary" style={{ justifyContent: 'center' }}>
          <RefreshCw size={16} /> Sync with Exchange
        </button>
      </div>

      {/* Right Column: Positions & Optimization */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
        
        {/* Portfolio Optimization Panel */}
        <div className="card" style={{ flexShrink: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div className="section-title" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <PieChart size={18} /> MPT Optimal Allocation (Max Sharpe)
            </div>
            <button className="btn btn-primary btn-sm" onClick={handleOptimize} disabled={optimizing}>
              {optimizing ? <Activity size={14} className="animate-spin" /> : <RefreshCw size={14} />}
              Calculate Optimal Weights
            </button>
          </div>

          {optimalAlloc ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              <div>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: 'var(--text-secondary)' }}>Target Weights</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {Object.entries(optimalAlloc.weights).map(([sym, weight]: any) => (
                    <div key={sym} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ width: '80px', fontSize: '13px', fontWeight: 'bold' }}>{sym.split('/')[0]}</div>
                      <div style={{ flex: 1, height: '8px', background: 'var(--bg-secondary)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${weight * 100}%`, background: 'var(--accent-cyan)', transition: 'width 1s ease' }}></div>
                      </div>
                      <div style={{ width: '40px', fontSize: '13px', textAlign: 'right' }}>{(weight * 100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: 'var(--text-secondary)' }}>Expected Annual Performance</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Expected Return</span>
                    <span className="text-positive" style={{ fontWeight: 'bold' }}>{(optimalAlloc.performance.expected_annual_return * 100).toFixed(1)}%</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Volatility (Risk)</span>
                    <span className="text-negative" style={{ fontWeight: 'bold' }}>{(optimalAlloc.performance.annual_volatility * 100).toFixed(1)}%</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border)', paddingTop: '12px', marginTop: '4px' }}>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Sharpe Ratio</span>
                    <span style={{ fontWeight: 'bold', color: 'var(--accent-indigo)' }}>{optimalAlloc.performance.sharpe_ratio}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-muted" style={{ padding: '30px 0', textAlign: 'center', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
              Click 'Calculate Optimal Weights' to run the PyPortfolioOpt Engine.
            </div>
          )}
        </div>

        {/* Positions Table */}
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div className="section-title">Active Positions</div>
          
          <table className="table" style={{ marginTop: '16px' }}>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Side</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>Size</th>
                <th>P&L</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 'bold' }}>BTC/USDT</td>
                <td><Badge variant="green">LONG</Badge></td>
                <td>$65,400.00</td>
                <td>$67,234.50</td>
                <td>0.15 BTC</td>
                <td className="text-positive">+$275.17</td>
                <td>
                  <button className="btn btn-sm" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }} onClick={async () => {
                    await closePaperTrade(1, 67234.50);
                    alert('Trade Closed! Evolution Agent is analyzing the post-mortem...');
                  }}>Close</button>
                </td>
              </tr>
              <tr>
                <td style={{ fontWeight: 'bold' }}>ETH/USDT</td>
                <td><Badge variant="green">LONG</Badge></td>
                <td>$3,300.00</td>
                <td>$3,456.20</td>
                <td>2.5 ETH</td>
                <td className="text-positive">+$390.50</td>
                <td>
                  <button className="btn btn-sm" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)' }}>Close</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
