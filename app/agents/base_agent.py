"""
base_agent.py – Abstract base class for all CryptoKali agents.

Every concrete agent must:
  • Declare `name` and `description` properties.
  • Implement `analyze(context: dict) -> dict`.

The base class provides:
  • `run_with_timeout(context, timeout_seconds)` – wraps analyze() in a
    concurrent.futures thread with a hard timeout.
  • `get_status()` – returns name, last_run timestamp, last_result, and
    the last error string if any.
  • Structured logging via the standard `logging` module.
"""

import logging
import time
import traceback
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for CryptoKali trading agents.

    Sub-classes must implement `name`, `description`, and `analyze`.
    """

    # ── State tracking ───────────────────────────────────────────────────────
    _last_run: Optional[str] = None
    _last_result: Optional[Dict[str, Any]] = None
    _last_error: Optional[str] = None

    # ── Identity ─────────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what this agent does."""

    # ── Core logic ───────────────────────────────────────────────────────────

    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent's analysis.

        Parameters
        ----------
        context : dict
            Arbitrary data the caller wants to pass in
            (e.g. symbol, df, positions …).

        Returns
        -------
        dict
            Agent-specific result.  Must always contain at least the key
            ``"agent"`` with value ``self.name``.
        """

    # ── Timeout wrapper ──────────────────────────────────────────────────────

    def run_with_timeout(
        self,
        context: Dict[str, Any],
        timeout_seconds: float = 30,
    ) -> Dict[str, Any]:
        """
        Call `analyze(context)` in a thread; raise if it takes longer than
        `timeout_seconds`.

        On success  → stores result in `_last_result`.
        On failure  → stores traceback in `_last_error`, returns error dict.
        """
        start = time.monotonic()
        self._last_run = datetime.now(timezone.utc).isoformat()

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.analyze, context)
            try:
                result: Dict[str, Any] = future.result(timeout=timeout_seconds)
                self._last_result = result
                self._last_error = None
                elapsed = time.monotonic() - start
                logger.debug(
                    "Agent %s finished in %.2fs", self.name, elapsed
                )
                return result

            except FuturesTimeout:
                msg = (
                    f"Agent '{self.name}' timed out after {timeout_seconds}s"
                )
                logger.error(msg)
                self._last_error = msg
                future.cancel()
                return self._error_result(msg)

            except Exception:
                tb = traceback.format_exc()
                logger.error(
                    "Agent '%s' raised an exception:\n%s", self.name, tb
                )
                self._last_error = tb
                return self._error_result(tb)

    # ── Status ───────────────────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Return a snapshot of this agent's runtime state."""
        return {
            "agent": self.name,
            "description": self.description,
            "last_run": self._last_run,
            "last_result": self._last_result,
            "error": self._last_error,
            "healthy": self._last_error is None,
        }

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _error_result(self, message: str) -> Dict[str, Any]:
        """Build a standardised error result dict."""
        return {
            "agent": self.name,
            "error": message,
            "success": False,
        }
