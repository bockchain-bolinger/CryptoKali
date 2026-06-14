'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Radio,
  LineChart,
  MessageSquare,
  Briefcase,
  Bot,
  History,
  Settings,
  Wifi,
  WifiOff,
  BarChart2,
  Activity
} from 'lucide-react';
import { ToastProvider } from '@/components/ui/Toast';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [btcPrice, setBtcPrice] = useState('67,234.50');
  const [ethPrice, setEthPrice] = useState('3,456.20');
  const [connected, setConnected] = useState(true);

  // Simulate live ticker updates
  useEffect(() => {
    const interval = setInterval(() => {
      setBtcPrice((67200 + Math.random() * 100).toFixed(2));
      setEthPrice((3450 + Math.random() * 20).toFixed(2));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={18} /> },
    { name: 'Arbitrage', path: '/arbitrage', icon: <Activity size={18} /> },
    { name: 'Signals', path: '/signals', icon: <Radio size={18} /> },
    { name: 'Chart', path: '/chart/BTC-USDT', icon: <LineChart size={18} /> },
    { name: 'Macro & Academy', path: '/macro', icon: <BarChart2 size={18} /> },
    { name: 'AI Chat', path: '/chat', icon: <MessageSquare size={18} /> },
    { name: 'Portfolio', path: '/portfolio', icon: <Briefcase size={18} /> },
    { name: 'Agents', path: '/agents', icon: <Bot size={18} /> },
    { name: 'Backtest', path: '/backtest', icon: <History size={18} /> },
    { name: 'Settings', path: '/settings', icon: <Settings size={18} /> },
  ];

  return (
    <html lang="en">
      <head>
        <title>CryptoKali Pro</title>
        <meta name="description" content="Crypto Trading Dashboard" />
      </head>
      <body>
        <div className="sidebar">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">K</div>
            <div className="sidebar-logo-text">CryptoKali Pro</div>
          </div>
          <nav className="sidebar-nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                href={item.path}
                className={pathname === item.path || pathname.startsWith(item.path) && item.path !== '/' ? 'active' : ''}
              >
                {item.icon}
                {item.name}
              </Link>
            ))}
          </nav>
          <div className="sidebar-footer">
            v1.0.0-beta • Connected
          </div>
        </div>

        <div className="topbar">
          <div style={{ display: 'flex', gap: '16px' }}>
            <div className="ticker-item">
              <span className="ticker-symbol">BTC/USDT</span>
              <span className="ticker-price text-positive">${btcPrice}</span>
            </div>
            <div className="ticker-item">
              <span className="ticker-symbol">ETH/USDT</span>
              <span className="ticker-price text-positive">${ethPrice}</span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="live-dot" data-tooltip="Live Data"></div>
            {connected ? (
              <Wifi size={18} color="var(--green)" />
            ) : (
              <WifiOff size={18} color="var(--red)" />
            )}
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-purple))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
              U
            </div>
          </div>
        </div>

        <main className="main-content">
          <ToastProvider>
            {children}
          </ToastProvider>
        </main>
      </body>
    </html>
  );
}
