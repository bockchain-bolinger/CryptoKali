"use client";

import { useEffect, useState } from "react";
import { fetchMacro, fetchOnchain } from "@/lib/api";
import { TrendingUp, TrendingDown, DollarSign, Activity, AlertCircle, Link, BarChart2 } from "lucide-react";

export default function MacroPage() {
  const [macro, setMacro] = useState<any>(null);
  const [onchain, setOnchain] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [m, o] = await Promise.all([fetchMacro(), fetchOnchain()]);
        setMacro(m);
        setOnchain(o);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
    const interval = setInterval(loadData, 60000); // refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex items-center space-x-3 text-indigo-400">
          <Activity className="animate-spin w-6 h-6" />
          <span className="text-lg font-medium tracking-wider">Syncing Global Data...</span>
        </div>
      </div>
    );
  }

  // Futuristic Design components
  return (
    <div className="space-y-8 pb-10 fade-in">
      {/* Header */}
      <div className="flex justify-between items-end border-b border-white/10 pb-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-indigo-500 tracking-tight">
            Macro & On-Chain Analytics
          </h1>
          <p className="text-gray-400 mt-2 text-sm tracking-wide">
            Master the global economy. Understand cause and effect to maximize trading profit.
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Global Liquidity Status</div>
          <div className={`text-xl font-bold ${macro?.crypto_impact.includes('Bullish') ? 'text-green-400' : macro?.crypto_impact.includes('Bearish') ? 'text-red-400' : 'text-yellow-400'}`}>
            {macro?.crypto_impact || "Neutral"}
          </div>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        
        {/* DXY Card */}
        <div className="card card-glass relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 to-cyan-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-gray-400 text-sm font-semibold uppercase tracking-wider">US Dollar Index (DXY)</h3>
              <div className="text-3xl font-bold text-white mt-1">{macro?.dxy?.value}</div>
            </div>
            <div className={`p-2 rounded-lg ${macro?.dxy?.change_pct > 0 ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            {macro?.dxy?.change_pct > 0 ? <TrendingUp className="w-4 h-4 text-red-400" /> : <TrendingDown className="w-4 h-4 text-green-400" />}
            <span className={macro?.dxy?.change_pct > 0 ? 'text-red-400' : 'text-green-400'}>
              {macro?.dxy?.change_pct > 0 ? '+' : ''}{macro?.dxy?.change_pct}%
            </span>
            <span className="text-gray-500">vs last close</span>
          </div>
        </div>

        {/* Treasury Yield Card */}
        <div className="card card-glass relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-400 to-pink-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-gray-400 text-sm font-semibold uppercase tracking-wider">13-W T-Bill (Yield)</h3>
              <div className="text-3xl font-bold text-white mt-1">{macro?.interest_rates?.value}%</div>
            </div>
            <div className={`p-2 rounded-lg ${macro?.interest_rates?.change_pct > 0 ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            {macro?.interest_rates?.change_pct > 0 ? <TrendingUp className="w-4 h-4 text-red-400" /> : <TrendingDown className="w-4 h-4 text-green-400" />}
            <span className={macro?.interest_rates?.change_pct > 0 ? 'text-red-400' : 'text-green-400'}>
              {macro?.interest_rates?.change_pct > 0 ? '+' : ''}{macro?.interest_rates?.change_pct}%
            </span>
            <span className="text-gray-500">proxy for FED rates</span>
          </div>
        </div>

        {/* TVL Card */}
        <div className="card card-glass relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-400 to-indigo-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-gray-400 text-sm font-semibold uppercase tracking-wider">DeFi TVL</h3>
              <div className="text-3xl font-bold text-white mt-1">${onchain?.total_tvl_billion}B</div>
            </div>
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Link className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
            <div className="bg-gray-800/50 p-2 rounded">
              <div className="text-gray-500">ETH</div>
              <div className="font-semibold">${onchain?.chains?.ethereum}B</div>
            </div>
            <div className="bg-gray-800/50 p-2 rounded">
              <div className="text-gray-500">SOL</div>
              <div className="font-semibold">${onchain?.chains?.solana}B</div>
            </div>
            <div className="bg-gray-800/50 p-2 rounded">
              <div className="text-gray-500">BTC</div>
              <div className="font-semibold">${onchain?.chains?.bitcoin}B</div>
            </div>
          </div>
        </div>
      </div>

      {/* Educational Section (Academy) */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
          <BarChart2 className="w-6 h-6 mr-3 text-cyan-400" />
          Interactive Learning: Cause & Effect
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Lesson 1 */}
          <div className="card card-glass border border-white/5 hover:border-cyan-500/30 transition-colors">
            <div className="flex items-start space-x-4">
              <div className="bg-cyan-500/20 p-3 rounded-full shrink-0">
                <AlertCircle className="w-6 h-6 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white mb-2">Why does the DXY matter?</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  The US Dollar Index (DXY) measures the strength of the dollar against other major currencies. 
                  Since Bitcoin is priced in dollars (BTC/USD), a <span className="text-green-400 font-bold">falling DXY</span> means the dollar is getting weaker, which automatically makes Bitcoin more valuable. 
                  <br/><br/>
                  <strong className="text-white">Rule of thumb:</strong> DXY goes UP = Crypto goes DOWN. Watch for DXY rejections at major resistance levels to enter long positions.
                </p>
              </div>
            </div>
          </div>

          {/* Lesson 2 */}
          <div className="card card-glass border border-white/5 hover:border-indigo-500/30 transition-colors">
            <div className="flex items-start space-x-4">
              <div className="bg-indigo-500/20 p-3 rounded-full shrink-0">
                <AlertCircle className="w-6 h-6 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white mb-2">Interest Rates (Yields)</h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  When the Federal Reserve raises interest rates, borrowing money becomes expensive. Investors pull their money out of risky assets like Crypto and put it into safe bonds.
                  <br/><br/>
                  <strong className="text-white">Current Status:</strong> With 13-W Yields at {macro?.interest_rates?.value}%, liquidity is {macro?.interest_rates?.value > 4 ? 'tight. The market is waiting for rate cuts to fuel the next massive bull run.' : 'loose. Perfect conditions for risk-on assets.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  );
}
