'use client';
import { useState, useRef, useEffect } from 'react';
import { StatCard } from '@/components/ui/StatCard';
import { Play, TrendingUp, AlertTriangle, Target, Activity } from 'lucide-react';

export default function BacktestPage() {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<any>(null);
  const chartContainerRef = useRef<HTMLDivElement>(null);

  const runBacktest = () => {
    setRunning(true);
    setResults(null);
    setTimeout(() => {
      setRunning(false);
      setResults({
        totalReturn: 34.2,
        sharpe: 1.8,
        maxDrawdown: -12.3,
        winRate: 61,
        trades: 47
      });
    }, 1500);
  };

  useEffect(() => {
    if (!results || !chartContainerRef.current) return;

    let chart: any = null;
    import('lightweight-charts').then(({ createChart }) => {
      if (!chartContainerRef.current) return;
      chartContainerRef.current.innerHTML = '';
      
      chart = createChart(chartContainerRef.current, {
        layout: { background: { color: 'transparent' }, textColor: '#94a3b8' },
        grid: { vertLines: { color: 'rgba(255,255,255,0.05)' }, horzLines: { color: 'rgba(255,255,255,0.05)' } },
        rightPriceScale: { borderColor: 'rgba(255,255,255,0.1)' },
        timeScale: { borderColor: 'rgba(255,255,255,0.1)' },
      });

      const areaSeries = chart.addAreaSeries({
        lineColor: '#6366f1',
        topColor: 'rgba(99, 102, 241, 0.4)',
        bottomColor: 'rgba(99, 102, 241, 0.0)',
        lineWidth: 2,
      });

      const data = [];
      let time = Math.floor(Date.now() / 1000) - 100 * 86400;
      let value = 10000;
      for (let i = 0; i < 100; i++) {
        value += (Math.random() - 0.45) * 500;
        data.push({ time, value });
        time += 86400;
      }
      
      areaSeries.setData(data);
      chart.timeScale().fitContent();
    });

    return () => {
      if (chart) chart.remove();
    };
  }, [results]);

  return (
    <div className="page animate-fade" style={{ display: 'flex', gap: '24px', height: 'calc(100vh - var(--topbar-height))' }}>
      {/* Left side: Form */}
      <div className="card" style={{ width: '320px', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
        <div className="section-title">Backtest Settings</div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflowY: 'auto' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Strategy</label>
            <select className="input">
              <option>AI Trend Follower</option>
              <option>Mean Reversion Pro</option>
              <option>Breakout Swarm</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Symbol</label>
            <input type="text" className="input" defaultValue="BTC/USDT" />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Timeframe</label>
            <select className="input">
              <option>1h</option>
              <option>4h</option>
              <option>1D</option>
            </select>
          </div>
          <div className="grid-2">
            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Start Date</label>
              <input type="date" className="input" defaultValue="2023-01-01" />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>End Date</label>
              <input type="date" className="input" defaultValue="2023-12-31" />
            </div>
          </div>
          
          <div style={{ borderTop: '1px solid var(--border)', margin: '8px 0', paddingTop: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '12px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Risk per Trade</span>
              <span>1.5%</span>
            </div>
            <input type="range" min="0.1" max="5" step="0.1" defaultValue="1.5" style={{ width: '100%' }} />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '12px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Stop Multiplier (ATR)</span>
              <span>2.0</span>
            </div>
            <input type="range" min="1" max="5" step="0.1" defaultValue="2.0" style={{ width: '100%' }} />
          </div>
        </div>

        <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '16px', padding: '12px' }} onClick={runBacktest} disabled={running}>
          {running ? <Activity size={16} className="animate-spin" /> : <Play size={16} />}
          {running ? 'Running Simulation...' : 'Run Backtest'}
        </button>
      </div>

      {/* Right side: Results */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
        {!results && !running && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
            Configure settings and run backtest to see results
          </div>
        )}
        
        {running && (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px' }}>
            <div className="skeleton" style={{ width: '100%', height: '120px' }}></div>
            <div className="skeleton" style={{ width: '100%', height: '300px' }}></div>
          </div>
        )}

        {results && (
          <div className="animate-slide">
            <div className="grid-4" style={{ marginBottom: '24px' }}>
              <StatCard title="Total Return" value={`+${results.totalReturn}%`} trend="up" icon={<TrendingUp size={20} />} />
              <StatCard title="Sharpe Ratio" value={results.sharpe} icon={<Activity size={20} />} />
              <StatCard title="Max Drawdown" value={`${results.maxDrawdown}%`} trend="down" icon={<AlertTriangle size={20} />} />
              <StatCard title="Win Rate" value={`${results.winRate}%`} change={`${results.trades} Trades`} icon={<Target size={20} />} />
            </div>

            <div className="card" style={{ marginBottom: '24px' }}>
              <div className="section-title">Equity Curve</div>
              <div ref={chartContainerRef} style={{ height: '300px', width: '100%' }}></div>
            </div>

            <div className="card">
              <div className="section-title">Recent Trades</div>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Entry</th>
                      <th>Exit</th>
                      <th>P&L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[1,2,3,4,5].map(i => (
                      <tr key={i}>
                        <td className="text-muted">2023-12-{30-i}</td>
                        <td className={i%2===0 ? 'text-negative' : 'text-positive'}>{i%2===0 ? 'SHORT' : 'LONG'}</td>
                        <td>$42,100</td>
                        <td>${42100 + (i%2===0 ? -500 : 800)}</td>
                        <td className={i%2===0 ? 'text-negative' : 'text-positive'}>{i%2===0 ? '-1.2%' : '+2.4%'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
