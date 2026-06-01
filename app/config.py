from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    SPOT_EXCHANGE: str = "binance"
    FUTURES_EXCHANGE: str = "binanceusdm"

    QUOTE: str = "USDT"

    TF_SIGNAL: str = "1h"
    TF_FILTER: str = "4h"
    LIMIT_SIGNAL: int = 400
    LIMIT_FILTER: int = 250

    MIN_QUOTE_VOLUME_USD_SPOT: float = 5000000.0
    MIN_QUOTE_VOLUME_USD_FUT: float = 20000000.0
    TOP_N: int = 30

    ACCOUNT_EQUITY: float = 10000.0
    RISK_PCT_PER_TRADE: float = 0.01

    LIQ_TEST_NOTIONAL_USD: float = 10000.0
    LIQ_MAX_SPREAD_PCT: float = 0.0015
    LIQ_MAX_SLIPPAGE_PCT_10K: float = 0.0025
    LIQ_REQUIRE_FILLED_10K: bool = True

    FEES_BPS: float = 6.0
    SLIPPAGE_BPS: float = 3.0

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    DISCORD_WEBHOOK_URL: str = ""
    GENERIC_WEBHOOK_URL: str = ""

    DB_PATH: str = "cryptokali.sqlite"

    SCAN_INTERVAL_SECONDS: int = 300

    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""


settings = Settings()

