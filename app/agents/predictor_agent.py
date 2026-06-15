import os
import joblib
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from app.data.feature_engineering import load_ohlcv_from_db, generate_features, get_latest_features

logger = logging.getLogger(__name__)

MODELS_DIR = "/home/artuirik/Schreibtisch/CryptoKali/artifacts/models"
os.makedirs(MODELS_DIR, exist_ok=True)

class PredictorAgent:
    def __init__(self):
        self.models = {} # Cache for loaded models
        
    def _get_model_path(self, symbol: str, timeframe: str) -> str:
        safe_sym = symbol.replace("/", "_")
        return os.path.join(MODELS_DIR, f"rf_model_{safe_sym}_{timeframe}.pkl")

    def train_model(self, symbol: str, timeframe: str = "1h") -> dict:
        """Trains a Random Forest classifier for the given symbol."""
        logger.info(f"Starting ML Training for {symbol} ({timeframe})...")
        
        # 1. Load Data
        df = load_ohlcv_from_db(symbol, timeframe, limit=10000)
        if df.empty or len(df) < 100:
            return {"status": "error", "message": "Not enough historical data to train."}
            
        # 2. Generate Features & Labels
        data = generate_features(df, target_periods=4) # Predict 4 periods ahead
        
        if len(data) < 50:
            return {"status": "error", "message": "Not enough data after feature engineering."}
            
        # 3. Prepare Train/Test sets
        # Exclude columns not used for prediction
        drop_cols = ['open', 'high', 'low', 'close', 'volume', 'target', 'future_return']
        feature_cols = [c for c in data.columns if c not in drop_cols]
        
        X = data[feature_cols]
        y = data['target']
        
        # Train on 80%
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # 4. Train Model
        clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        clf.fit(X_train, y_train)
        
        # 5. Evaluate (Simple Accuracy for MVP)
        train_acc = clf.score(X_train, y_train)
        test_acc = clf.score(X_test, y_test)
        
        # Feature Importance
        importances = clf.feature_importances_
        feature_importance = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
        
        # 6. Save Model
        model_path = self._get_model_path(symbol, timeframe)
        joblib.dump(clf, model_path)
        self.models[f"{symbol}_{timeframe}"] = clf
        
        logger.info(f"Training completed for {symbol}. Test Acc: {test_acc:.2f}")
        
        return {
            "status": "success",
            "symbol": symbol,
            "train_accuracy": round(train_acc, 3),
            "test_accuracy": round(test_acc, 3),
            "top_features": [{"feature": f[0], "importance": round(f[1], 3)} for f in feature_importance[:5]]
        }
        
    def predict(self, symbol: str, timeframe: str = "1h") -> dict:
        """Makes a prediction using the latest features."""
        model_key = f"{symbol}_{timeframe}"
        model_path = self._get_model_path(symbol, timeframe)
        
        # Load model if not in cache
        if model_key not in self.models:
            if not os.path.exists(model_path):
                return {"status": "error", "message": f"No model found for {symbol} ({timeframe}). Train it first."}
            self.models[model_key] = joblib.load(model_path)
            
        clf = self.models[model_key]
        
        # Get latest features
        features_dict = get_latest_features(symbol, timeframe)
        if not features_dict:
            return {"status": "error", "message": "Failed to generate live features."}
            
        # Ensure correct feature order (same as training)
        try:
            # We assume features_dict has all the expected keys. We drop raw price cols just in case.
            clean_features = {k: v for k, v in features_dict.items() if k not in ['open', 'high', 'low', 'close', 'volume']}
            
            # Predict
            X_live = pd.DataFrame([clean_features])
            
            # Use clf.feature_names_in_ to strictly align columns
            X_live = X_live[clf.feature_names_in_]
            
            prediction = clf.predict(X_live)[0]
            probabilities = clf.predict_proba(X_live)[0]
            
            bullish_prob = probabilities[1]
            bearish_prob = probabilities[0]
            
            return {
                "status": "success",
                "symbol": symbol,
                "prediction": "BULLISH" if prediction == 1 else "BEARISH",
                "confidence": round(float(bullish_prob if prediction == 1 else bearish_prob), 3),
                "probabilities": {
                    "bullish": round(float(bullish_prob), 3),
                    "bearish": round(float(bearish_prob), 3)
                }
            }
        except Exception as e:
            logger.error(f"Prediction failed for {symbol}: {e}")
            return {"status": "error", "message": str(e)}

# Global Instance
predictor = PredictorAgent()
