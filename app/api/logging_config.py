"""
Logging helpers for PRETO production observability.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any


SENSITIVE_KEYS = ("authorization", "token", "api_key", "password", "secret")


class JsonLogFormatter(logging.Formatter):
    """Format logs as JSON lines for container log collectors."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self._redact(str(record.getMessage())),
        }

        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, sort_keys=True)

    @staticmethod
    def _redact(message: str) -> str:
        redacted = message
        for key in SENSITIVE_KEYS:
            redacted = redacted.replace(key, f"{key[:2]}***")
        return redacted


def configure_logging() -> None:
    """Configure app logging from environment."""
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "text").lower()

    formatter: logging.Formatter
    if log_format == "json":
        formatter = JsonLogFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root.addHandler(handler)
