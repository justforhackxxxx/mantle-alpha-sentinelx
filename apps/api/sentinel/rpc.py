from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any


def rpc_call(rpc_url: str, method: str, params: list[Any] | None = None, timeout: float = 4.0) -> dict[str, Any]:
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or [],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        rpc_url,
        data=body,
        headers={"content-type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "method": method,
            "error": str(exc),
            "latencyMs": round((time.perf_counter() - started) * 1000),
        }

    if "error" in payload:
        return {
            "ok": False,
            "method": method,
            "error": payload["error"],
            "latencyMs": round((time.perf_counter() - started) * 1000),
        }

    return {
        "ok": True,
        "method": method,
        "result": payload.get("result"),
        "latencyMs": round((time.perf_counter() - started) * 1000),
    }


def probe_mantle_rpc(rpc_url: str | None) -> dict[str, Any]:
    if not rpc_url:
        return {
            "ok": False,
            "error": "rpc_url_not_configured",
        }

    chain = rpc_call(rpc_url, "eth_chainId")
    block = rpc_call(rpc_url, "eth_blockNumber")
    ok = bool(chain.get("ok") and block.get("ok"))

    return {
        "ok": ok,
        "rpcUrl": _redact_rpc_url(rpc_url),
        "chainId": int(chain["result"], 16) if chain.get("ok") else None,
        "latestBlock": int(block["result"], 16) if block.get("ok") else None,
        "latencyMs": max(chain.get("latencyMs", 0), block.get("latencyMs", 0)),
        "checks": {
            "eth_chainId": chain,
            "eth_blockNumber": block,
        },
    }


def _redact_rpc_url(rpc_url: str) -> str:
    if "://" not in rpc_url:
        return rpc_url
    scheme, rest = rpc_url.split("://", 1)
    host = rest.split("/", 1)[0]
    return f"{scheme}://{host}"

