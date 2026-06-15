Dann gehen wir systematisch in die Umsetzung der **Apex AI Core / MVP‑Stufe** und gießen das Architektur-Blueprint in konkrete, baubare Module.[1]

## Fokus jetzt: Apex AI Core (MVP)

Ziel der nächsten Phase:  
Ein stabiler Kern, der auf deiner bestehenden CryptoKali‑Architektur aufsetzt (Multi‑Agenten, SOR, Arbitrage, Whale-Tracking, Makro, Ollama, Next.js, PostgreSQL) und folgende Eigenschaften hat:[1]

- Saubere **Daten- & Feature-Pipeline** (historisch + live).
- **Apex Sentinel v1** (Risk- & Position Sizing mit PyPortfolioOpt/Riskfolio‑Lib).[2][3]
- **Apex Auditor v1** (Backtesting + Walk‑Forward, Promotion-Pipeline von Strategien, vorerst Paper-Trading).[4][5]
- Basic **Experiment-/Knowledge-Layer** (Research-Runs, Backtests, Metriken versioniert in Postgres).

Darauf können wir dann Apex Predictor/Evolution (ML/RL) iterativ aufsetzen.

***

## Phase 1 – Daten & Backtesting-Grundlage (1–2 Wochen)

### 1.1 Unified Market Data Layer

**Ziel:** Einheitliche Datenbasis für Backtests, Live-Signale und Research.

Kern-TODOs:

- Normalisierte Symbol-/Instrumenten-Tabelle (z.B. `assets` / `markets` in Postgres; Mapping: exchange_symbol → canonical_symbol).[1]
- Historische OHLCV/Trades für deine Kernmärkte (z.B. BTC/ETH Perps auf Binance/KuCoin/Bitget) laden und in dedizierten Tabellen speichern (z.B. `ohlcv_1m`, `ohlcv_5m`, `ohlcv_1h`).[1]
- Standardisiertes Schema für Live-Daten-Append (WebSockets → Ingestion-Service → DB).
- Resampling-Logik (Pandas o.ä.): aus Tick/1m → 5m/15m/1h für Modelle & Backtests.[6]

### 1.2 Apex Auditor v1 – einfache Backtesting-Engine

**Ziel:** Event-Driven Backtester, der deine aktuelle Strategie-Logik mit historischen Daten durchlaufen kann.

Kern-TODOs:

- Python-Modul `apex_auditor` mit:
  - Data-Feed-Interface (ähnlich Backtrader/LEAN: `next()` erhält Bar/State).[4][5]
  - Strategy-Interface (einheitliche Signatur für deine bestehenden Strategien: `on_bar(state) -> orders/signals`).
  - Broker-Simulation (Fees, Slippage, Partial Fills, Stop/Take-Orders).
- Ergebnis-Objekte: Trades, Equity-Curve, Metriken (PnL, Max Drawdown, Sharpe/Sortino, Win-Rate).
- Serialisierung der Backtests in DB: `backtests` + `backtest_metrics` + `backtest_trades`.

***

## Phase 2 – Apex Sentinel v1 (Risk & Portfolio) (1–2 Wochen)

### 2.1 Risk-Policies & Position Sizing

**Ziel:** Deine aktuelle Kelly/Win‑Rate‑Logik in einen generischen Risk-Agent gießen und um Portfolio-Kriterien erweitern.[1][2]

Kern-TODOs:

- Modul `apex_sentinel` mit:
  - Account- und Position-State (exchanges, balances, exposure pro Asset/Bucket).
  - Konfigurierbare Limits (max % Equity pro Trade, max Exposure pro Asset, max Leverage, max Daily Drawdown).
- Position Sizing:
  - Integration von PyPortfolioOpt / Riskfolio-Lib: Berechnung von optimalen Weights für ein Set von Signalen/Assets.[2][3]
  - Fallback/First Step: einfache Kelly/Volatility/Stop-Based-Größensteuerung.

### 2.2 Risk-Gates vor Execution

**Ziel:** Kein Signal geht direkt an SOR/Arbitrage, ohne durch Apex Sentinel.

Kern-TODOs:

- Klare Schnittstelle: `strategy_signal -> apex_sentinel -> execution_order`.
- Implementierung von Hard-Stops:
  - Daily Loss Limit.
  - Strategy-Level Max Drawdown → Auto-Deactivation.
- Logging aller Risk-Entscheidungen (für Apex Oracle/Auditor).

***

## Phase 3 – Experiment-Registry & Knowledge-Layer (1 Woche)

**Ziel:** Basis für „Autonomous Quant Research Lab“.

Kern-TODOs:

- Tabellen `experiments`, `experiment_runs`, `metrics`, `artifacts` in Postgres.
- Standard-JSON-Schema für:
  - Input (Dataset, Strategy/Model, Hyperparams).
  - Output (Metriken, Pfade zu Artefakten, Status).
- Wrapper-Funktionen:
  - `run_backtest_experiment(strategy_config)` → erstellt `experiment_run`, startet Apex Auditor, speichert Ergebnisse.
  - Hooks für Apex Oracle: Vertextung der wichtigsten Findings in natürlicher Sprache (Ollama).[1]

***

## Phase 4 – UI/UX-Hooks im Next.js Dashboard (1 Woche)

**Ziel:** Du siehst deine Research- und Risk-Welt in einem konsistenten UI.

Kern-TODOs:

- Views:
  - „Strategy Lab“: Liste der Strategien + Backtests + Promotion-Status.
  - „Risk Cockpit“: Aktuelle Limits, Exposures, Violations.
  - „Experiment Log“: Chronologische Liste aller Research-Runs.
- WebSocket/REST-Endpunkte im FastAPI-Backend für diese Daten.[1]

***

## Konkreter Startpunkt (heute/als Nächstes)

Um das sofort in Code zu gießen und dir maximalen Hebel zu geben, würde ich vorschlagen, zuerst **Phase 1.2 Apex Auditor v1** anzugehen:

- Du hast bereits:
  - Exchanges + CCXT + Live-Pipeline.[1]
- Du bekommst durch Apex Auditor:
  - Sofort mehr Hebel auf Research (alles, was du heute live handeln könntest, kannst du systematisch backtesten).
  - Eine solide Basis, auf der wir später sowohl ML (Predictor) als auch RL (Evolution) evaluieren können.[4][7]
