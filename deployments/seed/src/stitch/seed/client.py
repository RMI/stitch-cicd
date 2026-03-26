from __future__ import annotations

import json
import logging
from typing import Any, Iterable

import httpx
import time


from .openapi_validate import OpenAPIRequestValidator


logger = logging.getLogger("stitch.seed")


def post_payloads(
    client: httpx.Client,
    api_base_url: str,
    payloads: Iterable[dict[str, Any]],
    validator: OpenAPIRequestValidator,
) -> None:
    url = f"{api_base_url.rstrip('/')}/oil-gas-fields/"

    for payload in payloads:
        validator.validate(payload, client)
        logger.info("POST %s", url)
        logger.debug("Payload: %s", json.dumps(payload, ensure_ascii=False))

        resp = client.post(url, json=payload)
        logger.info("Response status=%s", resp.status_code)

        # body is debug-level (often large)
        try:
            body: Any = resp.json()
        except Exception:
            body = resp.text
        logger.debug(
            "Response body=%s",
            json.dumps(body, ensure_ascii=False)
            if isinstance(body, (dict, list))
            else body,
        )

        resp.raise_for_status()


def wait_for_api(base_url: str, retries: int = 30, delay: float = 2.0) -> None:
    url = f"{base_url.rstrip('/')}/health"
    logger.info("url: %s", url)

    for attempt in range(1, retries + 1):
        try:
            r = httpx.get(url, timeout=2.0)
            if 200 <= r.status_code < 300:
                logger.info("API ready after %s attempt(s)", attempt)
                return
            else:
                logger.info(
                    "API not ready (status %s), attempt %s of %s",
                    r.status_code,
                    attempt,
                    retries,
                )
        except Exception as e:
            logger.info(f"API not reachable ({e}), attempt {attempt}/{retries}")

        time.sleep(delay)

    raise RuntimeError("API did not become ready in time")
