import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def get_onchain_data() -> dict:
    """
    Fetches basic on-chain metrics via DefiLlama (free, no API key).
    - Total Value Locked (TVL)
    """
    try:
        r = requests.get("https://api.llama.fi/v2/chains", timeout=8)
        chains = r.json()
        
        total_tvl = sum([c.get("tvl", 0) for c in chains])
        btc_tvl = next((c.get("tvl", 0) for c in chains if c["name"] == "Bitcoin"), 0)
        eth_tvl = next((c.get("tvl", 0) for c in chains if c["name"] == "Ethereum"), 0)
        sol_tvl = next((c.get("tvl", 0) for c in chains if c["name"] == "Solana"), 0)
        
        return {
            "total_tvl_billion": round(total_tvl / 1_000_000_000, 2),
            "chains": {
                "bitcoin": round(btc_tvl / 1_000_000_000, 2),
                "ethereum": round(eth_tvl / 1_000_000_000, 2),
                "solana": round(sol_tvl / 1_000_000_000, 2)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to fetch DefiLlama data: {e}")
        return {
            "total_tvl_billion": 0,
            "chains": {"bitcoin": 0, "ethereum": 0, "solana": 0},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
