from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TradePlan(BaseModel):
    venue: str
    symbol: str
    strategy: str
    timeframe: str
    score: float
    entry: Optional[float] = None
    stop: Optional[float] = None
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    position_size_units: Optional[float] = None
    risk_usd: Optional[float] = None
    tags: List[str] = []
    components: Dict[str, float] = {}
    meta: Dict[str, Any] = {}
