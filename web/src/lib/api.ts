export const MOCK_FALLBACK = true;

// Vercel Setup: Use NEXT_PUBLIC_API_URL if available, else localhost
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://127.0.0.1:8000';

async function fetchWithFallback<T>(endpoint: string, mockData: T, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, cache: 'no-store' });
    if (!res.ok) throw new Error(`API returned ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn(`API call to ${endpoint} failed, using mock data. Error:`, err);
    if (MOCK_FALLBACK) return mockData;
    throw err;
  }
}

export async function fetchSignals() {
  const mock = [
    { id: 1, symbol: 'BTC/USDT', venue: 'Binance', strategy: 'Trend Following', score: 87, entry: 67200, stop: 66000, tp1: 68000, tp2: 69500, time: '2m ago', action: 'LONG' },
    { id: 2, symbol: 'ETH/USDT', venue: 'Binance', strategy: 'Mean Reversion', score: 74, entry: 3450, stop: 3400, tp1: 3520, tp2: 3600, time: '5m ago', action: 'LONG' },
    { id: 3, symbol: 'SOL/USDT', venue: 'Bybit', strategy: 'Breakout', score: 91, entry: 145, stop: 138, tp1: 155, tp2: 165, time: '12m ago', action: 'LONG' },
  ];
  try {
    const data = await fetchWithFallback('/api/v1/signals', { signals: mock });
    return data.signals || mock;
  } catch(e) { return mock; }
}

export async function fetchMarketOverview() {
  const mock = {
    fearGreed: 65,
    topGainers: [
      { symbol: 'SOL', change: '+5.2%' },
      { symbol: 'AVAX', change: '+4.1%' }
    ],
    topLosers: [
      { symbol: 'ADA', change: '-2.1%' }
    ]
  };
  try {
    const data: any = await fetchWithFallback('/api/v1/market/overview', null);
    if (!data) return mock;
    return {
      fearGreed: data.fear_greed?.value || 65,
      topGainers: [
        { symbol: 'BTC', change: data.btc?.change_24h ? `${data.btc.change_24h}%` : '+1.2%' },
        { symbol: 'ETH', change: data.eth?.change_24h ? `${data.eth.change_24h}%` : '+0.8%' }
      ],
      topLosers: [
        { symbol: 'BNB', change: data.bnb?.change_24h ? `${data.bnb.change_24h}%` : '-0.5%' }
      ]
    };
  } catch(e) { return mock; }
}

export async function fetchPortfolio() {
  const mock = {
    totalValue: 125430,
    dailyPnl: 2340,
    dailyPnlPercent: 1.9,
    winRate: 68,
    activePositions: 5,
    realizedPnl: 8200
  };
  return fetchWithFallback('/api/v1/portfolio', mock);
}

export async function fetchSentiment() {
  const mock = { score: 65, label: 'Greed' };
  try {
    const data: any = await fetchWithFallback('/api/v1/sentiment', { fear_greed: { value: 65, label: 'Greed' } });
    return { score: data?.fear_greed?.value || 65, label: data?.fear_greed?.label || 'Greed' };
  } catch(e) { return mock; }
}

export async function fetchNews(limit = 3) {
  const mock = [
    { id: 1, title: 'Bitcoin ETFs see record inflows as price breaks resistance', source: 'CoinDesk', time: '2 hours ago', impact: 'High' },
    { id: 2, title: 'Ethereum network upgrade scheduled for next month', source: 'CoinTelegraph', time: '4 hours ago', impact: 'Medium' }
  ];
  try {
    const data: any = await fetchWithFallback('/api/v1/news?limit=' + limit, { items: mock });
    return data.items || mock;
  } catch(e) { return mock; }
}

export async function analyzeSymbol(symbol: string, timeframe: string) {
  const mock = {
    analysis: `Bullish momentum detected for ${symbol} on ${timeframe}. RSI is at 58, indicating room for growth before hitting overbought territory. MACD crossover occurred 3 periods ago. Key resistance at next psychological level.`
  };
  try {
    const res: any = await fetchWithFallback('/api/v1/analyze', mock, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, timeframe })
    });
    return { analysis: res?.analysis?.reasoning || res.analysis || mock.analysis };
  } catch(e) { return mock; }
}

export async function sendChatMessage(sessionId: string, message: string) {
  const mock = {
    message: `Here's an analysis based on your request about "${message}". The current market conditions suggest a cautious approach with a slight bullish bias. I've checked the latest signals and our AI models show strong support at current levels.`
  };
  try {
    const res: any = await fetchWithFallback('/api/v1/chat', { response_text: mock.message }, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message, context: {} })
    });
    return { message: res.response_text || mock.message };
  } catch(e) { return mock; }
}

export async function fetchIndicators(symbol: string, timeframe: string) {
  const mock = {
    rsi: 58,
    macd: { value: 12.5, signal: 8.2, histogram: 4.3 },
    ema20: 65400,
    ema50: 63200
  };
  try {
    const res: any = await fetchWithFallback(`/api/v1/indicators/${encodeURIComponent(symbol)}?timeframe=${timeframe}`, { data: mock });
    return res.data || mock;
  } catch(e) { return mock; }
}

export async function fetchAgentStatus() {
  const mock = [
    { id: 'analyst', name: 'MarketAnalyst', status: 'Online', lastAction: 'BTC/USDT: Bullish bias (78%)', confidence: 78 },
    { id: 'risk', name: 'RiskAgent', status: 'Online', lastAction: 'Approved 3 trades today', confidence: 95 }
  ];
  try {
    const res: any = await fetchWithFallback('/api/v1/agents/status', { agents: mock });
    if (!res.agents) return mock;
    return res.agents.map((a: any) => ({
      id: a.name?.toLowerCase() || 'unknown',
      name: a.name,
      status: a.error ? 'Error' : 'Online',
      lastAction: a.last_result ? JSON.stringify(a.last_result).substring(0, 30) + '...' : 'Idle',
      confidence: 100
    }));
  } catch(e) { return mock; }
}

export async function placePaperTrade(trade: any) {
  return fetchWithFallback('/api/v1/orders/paper', { success: true, id: Math.floor(Math.random() * 1000) }, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(trade)
  });
}

export async function fetchPaperTrades() {
  const mock = [
    { id: 1, symbol: 'BTC/USDT', side: 'LONG', entry: 66500, current: 67234, pnl: 734, pnlPercent: 1.1, size: 0.1 },
    { id: 2, symbol: 'ETH/USDT', side: 'LONG', entry: 3300, current: 3456, pnl: 156, pnlPercent: 4.7, size: 2.5 }
  ];
  try {
    const res: any = await fetchWithFallback('/api/v1/orders/paper', { trades: mock });
    return res.trades || mock;
  } catch(e) { return mock; }
}

export async function fetchMacro() {
  const mock = {
    dxy: { value: 104.5, change_pct: -0.1 },
    interest_rates: { value: 5.25, change_pct: 0.0 },
    crypto_impact: "Neutral"
  };
  try {
    const res: any = await fetchWithFallback('/api/v1/macro', mock);
    return res || mock;
  } catch(e) { return mock; }
}

export async function fetchOnchain() {
  const mock = {
    total_tvl_billion: 150.5,
    chains: { bitcoin: 1.2, ethereum: 55.4, solana: 10.5 }
  };
  try {
    const res: any = await fetchWithFallback('/api/v1/onchain', mock);
    return res || mock;
  } catch(e) { return mock; }
}

export async function fetchWhaleData() {
  const mock = {
    cvd: { "BTC/USDT": 150000, "ETH/USDT": -25000 },
    recent_whales: [
      { id: 1, symbol: "BTC/USDT", side: "BUY", price: 67200, value_usdt: 250000, timestamp: new Date().toISOString() }
    ]
  };
  try {
    const res: any = await fetchWithFallback('/api/v1/whales', mock);
    return res || mock;
  } catch(e) { return mock; }
}

export async function fetchArbitrageSpreads() {
  const mock = {
    active: [
      { id: "mock-opp-1", symbol: "BTC/USDT", buy_exchange: "kucoin", sell_exchange: "binance", buy_price: 67100, sell_price: 67250, spread_pct: 0.22, timestamp: new Date().toISOString(), status: "pending_approval" },
      { id: "mock-opp-2", symbol: "ETH/USDT", buy_exchange: "bitget", sell_exchange: "binance", buy_price: 3450, sell_price: 3465, spread_pct: 0.43, timestamp: new Date().toISOString(), status: "radar_only" }
    ],
    history: []
  };
  try {
    const res: any = await fetchWithFallback('/api/v1/arbitrage', mock);
    return res || mock;
  } catch(e) { return mock; }
}

export async function rejectArbitrage(oppId: string) {
  return fetchWithFallback(`/api/v1/arbitrage/reject/${oppId}`, { status: "mocked_rejection" }, { method: "POST" });
}

export async function fetchHistoricalData(venue: string, symbol: string, timeframe: string, candles: number) {
  return fetchWithFallback('/api/v1/data/fetch-historical', { status: "success", fetched: candles }, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ venue, symbol, timeframe, candles })
  });
}

export async function runBacktest(venue: string, symbol: string, timeframe: string, strategy: string) {
  const mock = {
    venue, symbol, timeframe, strategy,
    trades: 124, winrate: 68.5, profit_factor: 1.8, max_dd: 4.2, expectancy: 0.5, net_pnl: 1450.50,
    meta_json: { equity_curve: [], trades: [] }
  };
  return fetchWithFallback('/api/v1/backtest/run', mock, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ venue, symbol, timeframe, strategy })
  });
}

export async function fetchRiskStatus() {
  return fetchWithFallback('/api/v1/risk/status', {
    circuit_breaker_active: false,
    max_risk_per_trade_pct: 2.0,
    max_daily_drawdown_pct: 5.0,
    max_open_positions: 3,
    current_open_positions: 1,
    status: "SAFE"
  });
}

export async function runExperiment(name: string, venue: string, symbol: string, timeframe: string, strategy: string) {
  return fetchWithFallback('/api/v1/lab/experiment/run', { status: "mocked" }, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, venue, symbol, timeframe, strategy })
  });
}

export async function fetchExperiments() {
  return fetchWithFallback('/api/v1/lab/experiments', []);
}

export async function promoteExperiment(runId: number, status: string) {
  return fetchWithFallback(`/api/v1/lab/experiment/${runId}/promote`, { status: "mocked" }, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
}

export async function trainMLModel(symbol: string, timeframe: string) {
  return fetchWithFallback('/api/v1/ml/train', { status: "mocked" }, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, timeframe })
  });
}

export async function predictML(symbol: string, timeframe: string = "1h") {
  return fetchWithFallback(`/api/v1/ml/predict/${encodeURIComponent(symbol)}?timeframe=${timeframe}`, { 
    status: "mocked", 
    prediction: "BULLISH",
    confidence: 0.85
  });
}

export async function optimizePortfolio(symbols: string[]) {
  return fetchWithFallback('/api/v1/portfolio/optimize', { status: "mocked" }, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbols })
  });
}

export async function scanArbitrage() {
  return fetchWithFallback('/api/v1/arbitrage/scan', [
    { symbol: 'BTC/USDT', buy_exchange: 'binance', sell_exchange: 'kucoin', buy_price: 65000, sell_price: 65050, net_spread_pct: 0.05, is_profitable: true }
  ]);
}

export async function closePaperTrade(tradeId: number, exitPrice: number) {
  return fetchWithFallback(`/api/v1/orders/paper/${tradeId}/close`, { status: "success" }, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ exit_price: exitPrice, symbol: "BTC/USDT", side: "LONG" }) // Mock details for now
  });
}

export async function getEvolutionLessons() {
  return fetchWithFallback('/api/v1/evolution/lessons', [
    { id: 1, trade_id: 12, symbol: 'BTC/USDT', pnl: 45.2, market_context: 'Trade: LONG BTC/USDT', lesson_learned: 'Successful momentum capture during high volume expansion.', timestamp: Date.now() }
  ]);
}

export async function simulateMacroScenario(dxyChange: number, rateChange: number) {
  return fetchWithFallback('/api/v1/macro/simulate', {
    status: 'success',
    projections: { btc_impact_pct: 12.5, eth_impact_pct: 15.6, tvl_impact_pct: 20.0, projected_btc: 73000, projected_eth: 4000, sentiment: 'Bullish' },
    report: 'Mock Report: Lower rates and a weaker dollar trigger a massive risk-on rally.'
  }, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dxy_change_pct: dxyChange, rate_change_pct: rateChange })
  });
}
