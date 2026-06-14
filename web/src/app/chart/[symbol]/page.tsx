'use client';
import { useState, useEffect, useRef } from 'react';
import { Search, Brain, Zap } from 'lucide-react';
import { analyzeSymbol } from '@/lib/api';

// Fallback for lightweight-charts rendering on client side only
export default function ChartPage({ params }: { params: { symbol: string } }) {
  const symbol = decodeURIComponent(params.symbol);
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [timeframe, setTimeframe] = useState('1h');
  const [analysisOpen, setAnalysisOpen] = useState(false);
  const [analysisText, setAnalysisText] = useState('');
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  // Indicators toggle
  const [indicators, setIndicators] = useState({
    ema20: true,
    ema50: true,
    bb: false,
    vwap: false,
    volume: true
  });

  const timeframes = ['1m', '5m', '15m', '1h', '4h', '1D'];

  useEffect(() => {
    let chart: any = null;
    let candlestickSeries: any = null;
    
    // Dynamically import lightweight-charts to prevent SSR issues
    import('lightweight-charts').then(({ createChart }) => {
      if (!chartContainerRef.current) return;
      
      chartContainerRef.current.innerHTML = '';
      
      chart = createChart(chartContainerRef.current, {
        layout: {
          background: { color: 'transparent' },
          textColor: '#94a3b8',
        },
        grid: {
          vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
          horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
        },
        crosshair: {
          mode: 0,
        },
        rightPriceScale: {
          borderColor: 'rgba(255, 255, 255, 0.1)',
        },
        timeScale: {
          borderColor: 'rgba(255, 255, 255, 0.1)',
          timeVisible: true,
        },
      });

      candlestickSeries = chart.addCandlestickSeries({
        upColor: '#22c55e',
        downColor: '#ef4444',
        borderVisible: false,
        wickUpColor: '#22c55e',
        wickDownColor: '#ef4444',
      });

      // Generate some mock OHLCV data
      const data = [];
      let time = Math.floor(Date.now() / 1000) - 30 * 3600;
      let open = 65000;
      for (let i = 0; i < 60; i++) {
        const close = open + (Math.random() - 0.45) * 1000;
        const high = Math.max(open, close) + Math.random() * 500;
        const low = Math.min(open, close) - Math.random() * 500;
        data.push({ time, open, high, low, close });
        open = close;
        time += 3600;
      }
      
      candlestickSeries.setData(data);

      if (indicators.ema20) {
        const ema20 = chart.addLineSeries({ color: '#22d3ee', lineWidth: 2 });
        ema20.setData(data.map(d => ({ time: d.time as number, value: (d.open + d.close) / 2 })));
      }
      if (indicators.ema50) {
        const ema50 = chart.addLineSeries({ color: '#f97316', lineWidth: 2 });
        ema50.setData(data.map(d => ({ time: d.time as number, value: (d.open + d.close) / 2 - 200 })));
      }

      chart.timeScale().fitContent();

      const handleResize = () => {
        if (chartContainerRef.current) {
          chart.applyOptions({ width: chartContainerRef.current.clientWidth });
        }
      };
      window.addEventListener('resize', handleResize);
      return () => {
        window.removeEventListener('resize', handleResize);
        chart.remove();
      };
    });
  }, [symbol, timeframe, indicators]);

  const handleAIAnalyse = async () => {
    setAnalysisOpen(true);
    setLoadingAnalysis(true);
    const res = await analyzeSymbol(symbol, timeframe);
    setAnalysisText(res.analysis);
    setLoadingAnalysis(false);
  };

  return (
    <div className="page animate-fade" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - var(--topbar-height))', padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexShrink: 0 }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '10px', color: 'var(--text-muted)' }} />
            <select className="input" style={{ paddingLeft: '36px', width: '200px', appearance: 'none', fontWeight: 700 }} value={symbol} onChange={() => {}}>
              <option value="BTC-USDT">BTC/USDT</option>
              <option value="ETH-USDT">ETH/USDT</option>
              <option value="BNB-USDT">BNB/USDT</option>
              <option value="SOL-USDT">SOL/USDT</option>
              <option value="ADA-USDT">ADA/USDT</option>
            </select>
          </div>
          
          <div style={{ display: 'flex', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', padding: '4px' }}>
            {timeframes.map(tf => (
              <button 
                key={tf}
                style={{
                  background: tf === timeframe ? 'var(--bg-card)' : 'transparent',
                  border: 'none',
                  color: tf === timeframe ? 'var(--text-primary)' : 'var(--text-secondary)',
                  padding: '4px 12px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: tf === timeframe ? 600 : 400,
                }}
                onClick={() => setTimeframe(tf)}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-primary" onClick={handleAIAnalyse}>
            <Brain size={16} /> AI Analysis
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '16px', flex: 1, minHeight: 0 }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '16px', minWidth: 0 }}>
          <div className="card" style={{ flex: 1, padding: '0', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', gap: '16px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', cursor: 'pointer' }}>
                <input type="checkbox" checked={indicators.ema20} onChange={e => setIndicators({...indicators, ema20: e.target.checked})} />
                <span style={{ color: '#22d3ee' }}>EMA 20</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', cursor: 'pointer' }}>
                <input type="checkbox" checked={indicators.ema50} onChange={e => setIndicators({...indicators, ema50: e.target.checked})} />
                <span style={{ color: '#f97316' }}>EMA 50</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', cursor: 'pointer' }}>
                <input type="checkbox" checked={indicators.bb} onChange={e => setIndicators({...indicators, bb: e.target.checked})} />
                <span style={{ color: 'var(--text-muted)' }}>Bollinger Bands</span>
              </label>
            </div>
            <div ref={chartContainerRef} style={{ flex: 1, width: '100%' }}></div>
          </div>
          
          <div className="card" style={{ height: '120px', padding: '12px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-secondary)' }}>RSI (14)</div>
            <div style={{ flex: 1, position: 'relative' }}>
              {/* Mock RSI chart space */}
              <div style={{ position: 'absolute', top: '30%', left: 0, right: 0, borderTop: '1px dashed rgba(239, 68, 68, 0.3)' }}></div>
              <div style={{ position: 'absolute', bottom: '30%', left: 0, right: 0, borderTop: '1px dashed rgba(34, 197, 94, 0.3)' }}></div>
              <svg width="100%" height="100%" preserveAspectRatio="none">
                <path d="M0,40 Q100,20 200,60 T400,30 T600,50 T800,40" fill="none" stroke="var(--accent-purple)" strokeWidth="2" />
              </svg>
            </div>
          </div>
        </div>

        {analysisOpen && (
          <div className="card animate-slide" style={{ width: '320px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div className="section-title" style={{ marginBottom: 0 }}>
                <Zap size={16} className="text-positive" /> AI Insights
              </div>
              <button className="btn-icon" style={{ width: '28px', height: '28px' }} onClick={() => setAnalysisOpen(false)}>×</button>
            </div>
            
            <div style={{ flex: 1, overflowY: 'auto', fontSize: '14px', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
              {loadingAnalysis ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div className="skeleton" style={{ height: '16px', width: '100%' }}></div>
                  <div className="skeleton" style={{ height: '16px', width: '100%' }}></div>
                  <div className="skeleton" style={{ height: '16px', width: '80%' }}></div>
                </div>
              ) : (
                <div>
                  <div style={{ marginBottom: '16px', padding: '12px', background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.2)', borderRadius: '8px', color: 'var(--text-primary)' }}>
                    <strong>Verdict: BULLISH</strong>
                  </div>
                  <p>{analysisText}</p>
                  
                  <div style={{ marginTop: '20px' }}>
                    <div style={{ fontSize: '12px', fontWeight: 600, marginBottom: '8px' }}>Key Levels</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span>Resistance</span>
                      <span className="text-negative">$68,500</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span>Support</span>
                      <span className="text-positive">$66,200</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
