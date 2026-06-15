'use client';
import { useState, useEffect } from 'react';
import { trainMLModel, predictML } from '@/lib/api';
import { Brain, Activity, Target, Zap, Network } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export default function MLPage() {
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [training, setTraining] = useState(false);
  const [fetching, setFetching] = useState(false);
  
  const [trainResult, setTrainResult] = useState<any>(null);
  const [prediction, setPrediction] = useState<any>(null);

  const handleTrain = async () => {
    setTraining(true);
    setTrainResult(null);
    try {
      const res = await trainMLModel(symbol, timeframe);
      setTrainResult(res);
      handlePredict(); // Automatically fetch prediction after training
    } catch (e) {
      alert("Error training model.");
    }
    setTraining(false);
  };

  const handlePredict = async () => {
    setFetching(true);
    try {
      const res = await predictML(symbol, timeframe);
      if (res.status !== "error") {
        setPrediction(res);
      }
    } catch (e) {
      console.error(e);
    }
    setFetching(false);
  };

  return (
    <div className="page animate-fade" style={{ display: 'flex', gap: '24px', height: 'calc(100vh - var(--topbar-height))' }}>
      
      {/* Left side: Controls */}
      <div className="card" style={{ width: '320px', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
        <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Network size={18} /> Model Training
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1 }}>
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Asset Symbol</label>
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
          
          <div style={{ padding: '16px', background: 'rgba(99, 102, 241, 0.05)', borderRadius: '8px', border: '1px solid rgba(99, 102, 241, 0.2)', marginTop: '8px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: 'var(--accent-indigo)' }}>Random Forest Pipeline</h4>
            <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Pulls OHLCV data from the database, engineers features (RSI, Volatility, Returns), and trains a model to predict 4 periods ahead.
            </p>
          </div>
        </div>

        <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '16px', padding: '12px' }} onClick={handleTrain} disabled={training}>
          {training ? <Activity size={16} className="animate-spin" /> : <Brain size={16} />}
          {training ? 'Training Model...' : 'Train Model'}
        </button>

        <button className="btn" style={{ width: '100%', justifyContent: 'center', marginTop: '8px', padding: '12px', background: 'var(--bg-secondary)', border: '1px solid var(--border)' }} onClick={handlePredict} disabled={fetching || training}>
          <Target size={16} /> Fetch Latest Prediction
        </button>
      </div>

      {/* Right side: Results */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
        
        {/* Prediction Panel */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: '160px', position: 'relative', overflow: 'hidden' }}>
          <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', zIndex: 1 }}>
            <Zap size={18} /> Live AI Prediction
          </div>
          
          {prediction ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1, zIndex: 1 }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '48px', fontWeight: '900', color: prediction.prediction === 'BULLISH' ? 'var(--green)' : 'var(--red)', textShadow: `0 0 20px ${prediction.prediction === 'BULLISH' ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}` }}>
                  {prediction.prediction}
                </div>
                <div style={{ fontSize: '16px', color: 'var(--text-secondary)', marginTop: '8px' }}>
                  Confidence: <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{(prediction.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1, color: 'var(--text-muted)', zIndex: 1 }}>
              No prediction active. Train the model first.
            </div>
          )}
          
          {/* Decorative background glow */}
          {prediction && (
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '300px', height: '300px', background: prediction.prediction === 'BULLISH' ? 'var(--green)' : 'var(--red)', opacity: 0.05, borderRadius: '50%', filter: 'blur(40px)', zIndex: 0, pointerEvents: 'none' }}></div>
          )}
        </div>

        {/* Training Results */}
        {trainResult && (
          <div className="card" style={{ flex: 1 }}>
            <div className="section-title">Model Performance ({trainResult.symbol})</div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
              <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Train Accuracy</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--text-primary)' }}>{(trainResult.train_accuracy * 100).toFixed(1)}%</div>
              </div>
              <div style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Test Accuracy (Holdout)</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--accent-cyan)' }}>{(trainResult.test_accuracy * 100).toFixed(1)}%</div>
              </div>
            </div>

            <h4 style={{ margin: '0 0 16px 0', fontSize: '14px', color: 'var(--text-secondary)' }}>Feature Importance</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {trainResult.top_features?.map((feat: any, idx: number) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ width: '120px', fontSize: '13px', color: 'var(--text-primary)' }}>{feat.feature}</div>
                  <div style={{ flex: 1, background: 'var(--bg-secondary)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${feat.importance * 100 * 3}%`, background: 'var(--accent-indigo)', height: '100%', borderRadius: '4px', transition: 'width 1s ease-out' }}></div>
                  </div>
                  <div style={{ width: '40px', fontSize: '12px', color: 'var(--text-muted)', textAlign: 'right' }}>
                    {(feat.importance * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
