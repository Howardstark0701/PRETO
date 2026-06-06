"""
Lightweight operational metrics for PRETO.

The collector intentionally avoids a hard dependency on prometheus-client so the
health and CI paths keep working in minimal local environments.
"""

from __future__ import annotations

from collections import defaultdict
from threading import Lock
from time import perf_counter
from typing import Dict, Tuple


class MetricsCollector:
    """Collect request counters and latency summaries."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: Dict[Tuple[str, str, int], int] = defaultdict(int)
        self._latency_total: Dict[Tuple[str, str], float] = defaultdict(float)
        self._latency_count: Dict[Tuple[str, str], int] = defaultdict(int)

    @staticmethod
    def now() -> float:
        return perf_counter()

    def record_request(self, method: str, path: str, status_code: int, duration: float) -> None:
        route = self._normalize_path(path)
        method = method.upper()

        with self._lock:
            self._requests[(method, route, status_code)] += 1
            self._latency_total[(method, route)] += duration
            self._latency_count[(method, route)] += 1

    def snapshot(self) -> dict:
        with self._lock:
            requests = dict(self._requests)
            latency_total = dict(self._latency_total)
            latency_count = dict(self._latency_count)

        total_requests = sum(requests.values())
        total_errors = sum(
            count for (_method, _route, status_code), count in requests.items()
            if status_code >= 500
        )

        return {
            "total_requests": total_requests,
            "total_5xx": total_errors,
            "requests": requests,
            "latency_total": latency_total,
            "latency_count": latency_count,
        }

    def to_prometheus(self) -> str:
        snapshot = self.snapshot()
        lines = [
            "# HELP preto_requests_total Total HTTP requests by method, route, and status.",
            "# TYPE preto_requests_total counter",
        ]

        for (method, route, status_code), count in sorted(snapshot["requests"].items()):
            lines.append(
                'preto_requests_total{'
                f'method="{method}",route="{route}",status="{status_code}"'
                f"}} {count}"
            )

        lines.extend([
            "# HELP preto_request_latency_seconds_total Total request latency in seconds.",
            "# TYPE preto_request_latency_seconds_total counter",
            "# HELP preto_request_latency_seconds_count Count of latency observations.",
            "# TYPE preto_request_latency_seconds_count counter",
        ])

        for (method, route), total in sorted(snapshot["latency_total"].items()):
            count = snapshot["latency_count"].get((method, route), 0)
            labels = f'method="{method}",route="{route}"'
            lines.append(f'preto_request_latency_seconds_total{{{labels}}} {total:.6f}')
            lines.append(f'preto_request_latency_seconds_count{{{labels}}} {count}')

        lines.extend([
            "# HELP preto_5xx_total Total HTTP 5xx responses.",
            "# TYPE preto_5xx_total counter",
            f'preto_5xx_total {snapshot["total_5xx"]}',
        ])

        return "\n".join(lines) + "\n"

    @staticmethod
    def _normalize_path(path: str) -> str:
        if path.startswith("/api/repos/user/") and path.endswith("/stats"):
            return "/api/repos/user/{username}/stats"
        if path.startswith("/api/repos/user/"):
            return "/api/repos/user/{username}"
        if path.startswith("/api/repos/") and len(path.strip("/").split("/")) == 4:
            return "/api/repos/{owner}/{repo_name}"
        if path.startswith("/api/auth/api-keys/"):
            return "/api/auth/api-keys/{key_id}"
        if path.startswith("/api/auth/saved-searches/"):
            return "/api/auth/saved-searches/{search_id}"
        return path


metrics_collector = MetricsCollector()
