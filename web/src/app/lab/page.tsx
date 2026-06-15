'use client';
import { useState, useEffect } from 'react';
import { fetchExperiments, runExperiment, promoteExperiment } from '@/lib/api';
import { Activity, Beaker, BrainCircuit, Play, History, ArrowUpRight } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export default function LabPage() {
  const [experiments, setExperiments] = useState<any[]>([]);
  const [running, setRunning] = useState(false);
  const [expName, setExpName] = useState('My First Test');
  const [venue, setVenue] = useState('binance');
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [strategy, setStrategy] = useState('MACD_Cross');

  const loadExperiments = async () => {
    const data = await fetchExperiments();
    setExperiments(data);
  };

  useEffect(() => {
    loadExperiments();
  }, []);

  const handleRun = async () => {
    setRunning(true);
    try {
      await runExperiment(expName, venue, symbol, timeframe, strategy);
      await loadExperiments();
    } catch (e) {
      alert("Error running experiment.");
    }
    setRunning(false);
  };

  const handlePromote = async (runId: number, status: string) => {
    try {
      await promoteExperiment(runId, status);
      await loadExperiments();
    } catch (e) {
      alert("Error promoting experiment.");
    }
  };

  return (
    <div className="page animate-fade" style={{ display: 'flex', gap: '24px', height: 'calc(100vh - var(--topbar-height))' }}>
      {/* Left side: Form */}
      <div className="card" style={{ width: '320px', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
        <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Beaker size={18} /> New Experiment
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflowY: 'auto' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Experiment Name</label>
            <input type="text" className="input" value={expName} onChange={e => setExpName(e.target.value)} />
          </div>
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
        </div>

        <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '16px', padding: '12px' }} onClick={handleRun} disabled={running}>
          {running ? <Activity size={16} className="animate-spin" /> : <Play size={16} />}
          {running ? 'Running Lab...' : 'Start Experiment'}
        </button>
      </div>

      {/* Right side: Registry */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <History size={18} /> Experiment Registry
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto', paddingRight: '8px' }}>
            {experiments.length === 0 && (
              <div className="text-muted" style={{ textAlign: 'center', marginTop: '40px' }}>No experiments run yet. Start one!</div>
            )}
            
            {experiments.map((exp: any) => (
              <div key={exp.id} style={{ background: 'var(--bg-secondary)', borderRadius: '12px', padding: '20px', border: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                  <div>
                    <h3 style={{ margin: '0 0 8px 0', color: 'var(--text-primary)', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {exp.experiment_name}
                      {exp.status === 'live' && <Badge variant="green">LIVE</Badge>}
                      {exp.status === 'paper' && <Badge variant="blue">PAPER</Badge>}
                      {exp.status === 'research' && <Badge variant="gray">RESEARCH</Badge>}
                    </h3>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      <Badge variant="blue">{exp.strategy}</Badge>
                      <Badge variant="gray">{exp.symbol}</Badge>
                      <Badge variant="gray">{exp.timeframe}</Badge>
                      <span className="text-muted" style={{ fontSize: '12px', alignSelf: 'center' }}>
                        {new Date(exp.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                    <div>
                      <div className={exp.metrics.net_pnl >= 0 ? 'text-positive' : 'text-negative'} style={{ fontSize: '20px', fontWeight: 'bold' }}>
                        {exp.metrics.net_pnl >= 0 ? '+' : ''}${exp.metrics.net_pnl?.toFixed(2)}
                      </div>
                      <div className="text-muted" style={{ fontSize: '12px' }}>
                        WR: {exp.metrics.winrate?.toFixed(1)}% | DD: {exp.metrics.max_dd?.toFixed(1)}%
                      </div>
                    </div>
                    {exp.status === 'research' && exp.metrics.net_pnl > 0 && (
                      <button className="btn btn-sm btn-primary" onClick={() => handlePromote(exp.id, 'paper')} style={{ fontSize: '11px', padding: '4px 8px' }}>
                        <ArrowUpRight size={14} /> Promote to Paper
                      </button>
                    )}
                  </div>
                </div>

                <div style={{ background: 'rgba(99, 102, 241, 0.05)', borderRadius: '8px', padding: '16px', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-indigo)', marginBottom: '8px', fontWeight: 'bold', fontSize: '14px' }}>
                    <BrainCircuit size={16} /> Apex Oracle (AI Finding)
                  </div>
                  <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.5', color: 'var(--text-secondary)' }}>
                    {exp.ai_finding || "Keine AI Analyse verfügbar."}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
