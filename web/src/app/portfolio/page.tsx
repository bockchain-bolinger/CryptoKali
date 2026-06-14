'use client';
import { useState, useEffect } from 'react';
import { fetchPortfolio, fetchPaperTrades } from '@/lib/api';
import { StatCard } from '@/components/ui/StatCard';
import { Badge } from '@/components/ui/Badge';
import { Wallet, TrendingUp, Percent, History, Activity, ShieldAlert } from 'lucide-react';

export default function PortfolioPage() {
  const [activeTab, setActiveTab] = useState('positions');
  const [portfolio, setPortfolio] = useState<any>(null);
  const [paperTrades, setPaperTrades] = useState<any[]>([]);

  useEffect(() => {
    async function load() {
      const port = await fetchPortfolio();
      const trades = await fetchPaperTrades();
      setPortfolio(port);
      setPaperTrades(trades);
    }
    load();
  }, []);

  if (!portfolio) return <div className="page"><div className="skeleton" style={{ height: '200px' }}></div></div>;

  return (
    <div className="page animate-fade">
      <div className="page-header">
        <h1>Portfolio</h1>
        <p>Manage your real and paper trading positions</p>
      </div>

      <div className="grid-4" style={{ marginBottom: '24px' }}>
        <StatCard 
          title="Total Value" 
          value={`$${portfolio.totalValue.toLocaleString()}`}
          icon={<Wallet size={20} />}
        />
        <StatCard 
          title="Open P&L" 
          value={`+$${portfolio.dailyPnl.toLocaleString()}`}
          changePercent={portfolio.dailyPnlPercent}
          trend="up"
          icon={<Activity size={20} />}
        />
        <StatCard 
          title="Realized P&L" 
          value={`+$${portfolio.realizedPnl.toLocaleString()}`}
          trend="up"
          icon={<TrendingUp size={20} />}
        />
        <StatCard 
          title="Win Rate" 
          value={`${portfolio.winRate}%`}
          icon={<Percent size={20} />}
        />
      </div>

      <div className="grid-3" style={{ marginBottom: '24px' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <div className="section-title" style={{ alignSelf: 'flex-start' }}>Risk Exposure</div>
          
          <div style={{ position: 'relative', width: '160px', height: '80px', overflow: 'hidden', marginTop: '20px' }}>
            <div style={{ position: 'absolute', top: 0, left: 0, width: '160px', height: '160px', borderRadius: '50%', border: '15px solid rgba(255,255,255,0.05)', borderBottomColor: 'transparent', borderRightColor: 'transparent', transform: 'rotate(-45deg)', boxSizing: 'border-box' }}></div>
            <div style={{ position: 'absolute', top: 0, left: 0, width: '160px', height: '160px', borderRadius: '50%', border: '15px solid var(--accent-cyan)', borderBottomColor: 'transparent', borderRightColor: 'transparent', transform: 'rotate(15deg)', transition: 'transform 1s ease-out', boxSizing: 'border-box' }}></div>
            <div style={{ position: 'absolute', bottom: '0', left: '50%', transform: 'translateX(-50%)', fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
              12.5%
            </div>
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px' }}>Capital at Risk</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '16px', background: 'rgba(34,211,238,0.1)', padding: '6px 12px', borderRadius: '20px', fontSize: '12px', color: 'var(--accent-cyan)' }}>
            <ShieldAlert size={14} /> Healthy Risk Level
          </div>
        </div>

        <div className="card" style={{ gridColumn: 'span 2' }}>
          <div className="section-title">Asset Allocation</div>
          <div style={{ height: '24px', display: 'flex', borderRadius: '12px', overflow: 'hidden', marginBottom: '16px' }}>
            <div style={{ width: '45%', background: '#F7931A' }} data-tooltip="BTC: 45%"></div>
            <div style={{ width: '30%', background: '#627EEA' }} data-tooltip="ETH: 30%"></div>
            <div style={{ width: '15%', background: '#14F195' }} data-tooltip="SOL: 15%"></div>
            <div style={{ width: '10%', background: '#26A17B' }} data-tooltip="USDT: 10%"></div>
          </div>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}><div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#F7931A' }}></div> BTC (45%)</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}><div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#627EEA' }}></div> ETH (30%)</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}><div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#14F195' }}></div> SOL (15%)</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}><div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#26A17B' }}></div> USDT (10%)</div>
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid var(--border)' }}>
          <button 
            style={{ padding: '16px 24px', background: 'transparent', border: 'none', borderBottom: activeTab === 'positions' ? '2px solid var(--accent-indigo)' : '2px solid transparent', color: activeTab === 'positions' ? 'var(--text-primary)' : 'var(--text-secondary)', fontWeight: 600, cursor: 'pointer' }}
            onClick={() => setActiveTab('positions')}
          >
            Live Positions
          </button>
          <button 
            style={{ padding: '16px 24px', background: 'transparent', border: 'none', borderBottom: activeTab === 'paper' ? '2px solid var(--accent-indigo)' : '2px solid transparent', color: activeTab === 'paper' ? 'var(--text-primary)' : 'var(--text-secondary)', fontWeight: 600, cursor: 'pointer' }}
            onClick={() => setActiveTab('paper')}
          >
            Paper Trades
          </button>
          <button 
            style={{ padding: '16px 24px', background: 'transparent', border: 'none', borderBottom: activeTab === 'history' ? '2px solid var(--accent-indigo)' : '2px solid transparent', color: activeTab === 'history' ? 'var(--text-primary)' : 'var(--text-secondary)', fontWeight: 600, cursor: 'pointer' }}
            onClick={() => setActiveTab('history')}
          >
            History <History size={14} style={{ display: 'inline', marginLeft: '4px' }} />
          </button>
        </div>

        <div className="table-wrapper" style={{ padding: '16px' }}>
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Side</th>
                <th>Size</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>P&L</th>
                <th>P&L %</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {paperTrades.map(trade => (
                <tr key={trade.id}>
                  <td style={{ fontWeight: 600 }}>{trade.symbol}</td>
                  <td><Badge variant={trade.side === 'LONG' ? 'green' : 'red'}>{trade.side}</Badge></td>
                  <td>{trade.size}</td>
                  <td>${trade.entry.toLocaleString()}</td>
                  <td>${trade.current.toLocaleString()}</td>
                  <td className={trade.pnl >= 0 ? 'text-positive' : 'text-negative'}>
                    {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toLocaleString()}
                  </td>
                  <td className={trade.pnlPercent >= 0 ? 'text-positive' : 'text-negative'}>
                    {trade.pnlPercent >= 0 ? '+' : ''}{trade.pnlPercent}%
                  </td>
                  <td>
                    <button className="btn btn-sm btn-danger">Close</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
