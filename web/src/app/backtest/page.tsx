'use client';
import { useState, useRef, useEffect } from 'react';
import { StatCard } from '@/components/ui/StatCard';
import { Play, TrendingUp, AlertTriangle, Target, Activity, Download } from 'lucide-react';
import { runBacktest, fetchHistoricalData } from '@/lib/api';

export default function BacktestPage() {
  const [running, setRunning] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [results, setResults] = useState<any>(null);
  
  const [venue, setVenue] = useState('binance');
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [strategy, setStrategy] = useState('MACD_Cross');
  
  const chartContainerRef = useRef<HTMLDivElement>(null);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await fetchHistoricalData(venue, symbol, timeframe, 1000);
      alert(`Erfolgreich ${res.fetched || 1000} Kerzen für ${symbol} heruntergeladen.`);
    } catch(e) {
      alert("Fehler beim Download");
    }
    setDownloading(false);
  };

  const handleRunBacktest = async () => {
    setRunning(true);
    setResults(null);
    try {
      const data = await runBacktest(venue, symbol, timeframe, strategy);
      if (data.error) {
        alert(data.error);
      } else {
        setResults(data);
      }
    } catch (e) {
      alert("Fehler beim Backtesting.");
    }
    setRunning(false);
  };

  useEffect(() => {
    if (!results || !results.meta_json || !chartContainerRef.current) return;

    let chart: any = null;
    import('lightweight-charts').then(({ createChart }) => {
      if (!chartContainerRef.current) return;
      chartContainerRef.current.innerHTML = '';
      
      chart = createChart(chartContainerRef.current, {
        layout: { background: { color: 'transparent' }, textColor: '#94a3b8' },
        grid: { vertLines: { color: 'rgba(255,255,255,0.05)' }, horzLines: { color: 'rgba(255,255,255,0.05)' } },
        rightPriceScale: { borderColor: 'rgba(255,255,255,0.1)' },
        timeScale: { borderColor: 'rgba(255,255,255,0.1)', timeVisible: true },
      });

      const areaSeries = chart.addAreaSeries({
        lineColor: '#6366f1',
        topColor: 'rgba(99, 102, 241, 0.4)',
        bottomColor: 'rgba(99, 102, 241, 0.0)',
        lineWidth: 2,
      });

      const curve = results.meta_json.equity_curve || [];
      if (curve.length > 0) {
        // lightweight-charts needs time in seconds
        const data = curve.map((c: any) => ({
          time: Math.floor(c.time / 1000), 
          value: c.capital
        }));
        // Sort to ensure ascending order
        data.sort((a: any, b: any) => a.time - b.time);
        
        // Remove duplicates
        const uniqueData = data.filter((v: any, i: number, a: any[]) => a.findIndex(t => t.time === v.time) === i);
        
        areaSeries.setData(uniqueData);
        chart.timeScale().fitContent();
      }
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
            <select className="input" value={strategy} onChange={e => setStrategy(e.target.value)}>
              <option value="MACD_Cross">MACD Crossover</option>
              <option value="TrendFollowing">Trend Following (Coming Soon)</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Venue</label>
            <select className="input" value={venue} onChange={e => setVenue(e.target.value)}>
              <option value="binance">Binance</option>
              <option value="kucoin">KuCoin</option>
              <option value="bitget">Bitget</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Symbol</label>
            <input type="text" className="input" value={symbol} onChange={e => setSymbol(e.target.value)} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Timeframe</label>
            <select className="input" value={timeframe} onChange={e => setTimeframe(e.target.value)}>
              <option value="15m">15m</option>
              <option value="1h">1h</option>
              <option value="4h">4h</option>
              <option value="1d">1D</option>
            </select>
          </div>
          
          <div style={{ borderTop: '1px solid var(--border)', margin: '8px 0', paddingTop: '16px' }}>
             <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'center' }} onClick={handleDownload} disabled={downloading}>
              {downloading ? <Activity size={16} className="animate-spin" /> : <Download size={16} />}
              {downloading ? 'Downloading...' : 'Fetch Historical Data'}
            </button>
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px', textAlign: 'center' }}>
              Requires data in DB before testing.
            </p>
          </div>
        </div>

        <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '16px', padding: '12px' }} onClick={handleRunBacktest} disabled={running}>
          {running ? <Activity size={16} className="animate-spin" /> : <Play size={16} />}
          {running ? 'Running Simulation...' : 'Run Backtest'}
        </button>
      </div>

      {/* Right side: Results */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
        {!results && !running && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
            Configure settings, fetch data, and run backtest to see results
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
              <StatCard title="Net P&L" value={`$${results.net_pnl.toFixed(2)}`} trend={results.net_pnl >= 0 ? 'up' : 'down'} icon={<TrendingUp size={20} />} />
              <StatCard title="Profit Factor" value={results.profit_factor === null ? '∞' : results.profit_factor.toFixed(2)} icon={<Activity size={20} />} />
              <StatCard title="Max Drawdown" value={`${results.max_dd.toFixed(2)}%`} trend="down" icon={<AlertTriangle size={20} />} />
              <StatCard title="Win Rate" value={`${results.winrate.toFixed(1)}%`} change={`${results.trades} Trades`} icon={<Target size={20} />} />
            </div>

            <div className="card" style={{ marginBottom: '24px' }}>
              <div className="section-title">Equity Curve (Capital: $10,000)</div>
              <div ref={chartContainerRef} style={{ height: '300px', width: '100%' }}></div>
            </div>

            <div className="card">
              <div className="section-title">Recent Trades</div>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Exit Time</th>
                      <th>Entry Price</th>
                      <th>Exit Price</th>
                      <th>P&L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(results.meta_json?.trades || []).slice(-10).reverse().map((t: any, i: number) => (
                      <tr key={i}>
                        <td className="text-muted">{new Date(t.exit_time).toLocaleString()}</td>
                        <td>${t.entry_price.toFixed(2)}</td>
                        <td>${t.exit_price.toFixed(2)}</td>
                        <td className={t.pnl >= 0 ? 'text-positive' : 'text-negative'}>
                          {t.pnl >= 0 ? '+' : ''}{t.pnl.toFixed(2)} ({t.pnl_pct.toFixed(2)}%)
                        </td>
                      </tr>
                    ))}
                    {(results.meta_json?.trades || []).length === 0 && (
                      <tr><td colSpan={4} style={{textAlign: 'center'}} className="text-muted">No trades executed</td></tr>
                    )}
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
