'use client';
import { useState, useEffect } from 'react';
import { fetchMarketOverview, fetchPortfolio, fetchSignals, fetchNews, fetchWhaleData } from '@/lib/api';
import { StatCard } from '@/components/ui/StatCard';
import { FearGreedGauge } from '@/components/ui/FearGreedGauge';
import { Badge } from '@/components/ui/Badge';
import { ScoreBar } from '@/components/ui/ScoreBar';
import { Wallet, TrendingUp, Percent, Target } from 'lucide-react';
import Link from 'next/link';

export default function Dashboard() {
  const [data, setData] = useState<{
    portfolio: any,
    market: any,
    signals: any[],
    news: any[],
    whales: any
  } | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [portfolio, market, signals, news, whales] = await Promise.all([
          fetchPortfolio(),
          fetchMarketOverview(),
          fetchSignals(),
          fetchNews(3),
          fetchWhaleData()
        ]);
        setData({ portfolio, market, signals: signals.slice(0, 5), news, whales });
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
  }, []);

  if (!data) return <div className="page"><div className="skeleton" style={{ height: '200px' }}></div></div>;

  return (
    <div className="page animate-fade">
      <div className="page-header">
        <h1>Dashboard Overview</h1>
        <p>Your portfolio and market at a glance</p>
      </div>

      <div className="grid-4" style={{ marginBottom: '24px' }}>
        <StatCard 
          title="Portfolio Value" 
          value={`$${data.portfolio.totalValue.toLocaleString()}`}
          change={`+$${data.portfolio.dailyPnl}`}
          changePercent={data.portfolio.dailyPnlPercent}
          trend="up"
          icon={<Wallet size={20} />}
        />
        <StatCard 
          title="Daily P&L" 
          value={`+$${data.portfolio.dailyPnl.toLocaleString()}`}
          change="Strong performance today"
          trend="up"
          icon={<TrendingUp size={20} />}
        />
        <StatCard 
          title="Win Rate" 
          value={`${data.portfolio.winRate}%`}
          change="Based on last 30 days"
          icon={<Percent size={20} />}
        />
        <StatCard 
          title="Active Positions" 
          value={data.portfolio.activePositions}
          change="Monitoring closely"
          icon={<Target size={20} />}
        />
      </div>

      <div className="grid-3" style={{ marginBottom: '24px' }}>
        <div className="card">
          <div className="section-title">Market Sentiment</div>
          <div style={{ display: 'flex', justifyContent: 'center', margin: '20px 0' }}>
            <FearGreedGauge value={data.market.fearGreed} />
          </div>
        </div>
        
        <div className="card" style={{ gridColumn: 'span 2' }}>
          <div className="section-title">Top Signals</div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Action</th>
                  <th>Score</th>
                  <th>Entry</th>
                  <th>Target</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {data.signals.map((sig, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600 }}>{sig.symbol}</td>
                    <td>
                      <Badge variant={sig.action === 'LONG' ? 'green' : 'red'}>{sig.action}</Badge>
                    </td>
                    <td style={{ minWidth: '100px' }}>
                      <ScoreBar score={sig.score} />
                    </td>
                    <td>${sig.entry}</td>
                    <td>${sig.tp1}</td>
                    <td className="text-muted">{sig.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: '12px', textAlign: 'right' }}>
            <Link href="/signals" className="text-secondary" style={{ fontSize: '13px', textDecoration: 'none' }}>View all signals &rarr;</Link>
          </div>
        </div>
      </div>

      <div>
        <div className="section-title">Recent News</div>
        <div className="grid-3">
          {data.news.map((item, i) => (
            <div key={i} className="card-glass" style={{ padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className="text-muted" style={{ fontSize: '12px' }}>{item.source} • {item.time}</span>
                <Badge variant={item.impact === 'High' ? 'red' : item.impact === 'Medium' ? 'yellow' : 'blue'}>
                  {item.impact} Impact
                </Badge>
              </div>
              <h3 style={{ fontSize: '14px', fontWeight: 600, lineHeight: 1.4 }}>{item.title}</h3>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: '24px' }}>
        <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '20px' }}>🐳</span> Live Whale Radar
        </div>
        <div className="grid-2" style={{ gap: '24px' }}>
          {/* CVD Bar */}
          <div className="card-glass" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '16px' }}>Cumulative Volume Delta (BTC/USDT)</h3>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: data.whales?.cvd?.['BTC/USDT'] > 0 ? 'var(--green)' : 'var(--red)', marginBottom: '8px' }}>
              {data.whales?.cvd?.['BTC/USDT'] > 0 ? '+' : ''}${(data.whales?.cvd?.['BTC/USDT'] || 0).toLocaleString()}
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {data.whales?.cvd?.['BTC/USDT'] > 0 ? 'Aggressive Buyers are in control.' : 'Aggressive Sellers are in control.'}
            </p>
          </div>
          
          {/* Recent Whale Alerts */}
          <div className="card-glass" style={{ padding: '20px' }}>
             <h3 style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '16px' }}>Recent Whale Trades (&gt; $50k)</h3>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
               {data.whales?.recent_whales?.slice(0, 3).map((w: any, idx: number) => (
                 <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                   <div>
                     <Badge variant={w.side === 'BUY' ? 'green' : 'red'}>{w.side}</Badge>
                     <span style={{ marginLeft: '8px', fontWeight: 'bold' }}>{w.symbol}</span>
                   </div>
                   <div style={{ fontWeight: 'bold' }}>
                     ${w.value_usdt.toLocaleString()}
                   </div>
                 </div>
               ))}
               {(!data.whales?.recent_whales || data.whales.recent_whales.length === 0) && (
                 <div className="text-muted" style={{ fontSize: '13px' }}>Waiting for whale activity...</div>
               )}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
