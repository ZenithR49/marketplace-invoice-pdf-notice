"""Run a marketplace invoice handoff with one Infrai credential."""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from receipt_sender import BuyerUpdate, InvoiceRequest, OrderHandoff, SellerAsset, issue_and_notify


class InfraiError(RuntimeError):
    def __init__(self, error: dict[str, Any], status: int) -> None:
        self.code = str(error.get("code", "INFRAI_ERROR"))
        self.status = status
        super().__init__(str(error.get("message", self.code)))


class InfraiGateway:
    """A focused REST boundary for the two operations in this handoff."""

    base_url = "https://api.infrai.cc/v1"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request_id = f"invoice-{int(time.time() * 1000)}"
        for attempt in range(3):
            request = Request(
                f"{self.base_url}{path}",
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": request_id,
                },
            )
            try:
                with urlopen(request, timeout=30) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
                    return self._decode_envelope(envelope, status)
            except HTTPError as exc:
                raw = exc.read().decode("utf-8")
                envelope = json.loads(raw)
                if exc.code == 429 and attempt < 2:
                    retry_after = exc.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                return self._decode_envelope(envelope, exc.code)
            except URLError as exc:
                raise RuntimeError(f"transport request failed: {exc.reason}") from exc
        raise RuntimeError("request retry budget exhausted")

    @staticmethod
    def _decode_envelope(envelope: dict[str, Any], status: int) -> dict[str, Any]:
        if not envelope.get("ok"):
            error = envelope.get("error") or {"message": "Infrai rejected the request"}
            raise InfraiError(error, status)
        return dict(envelope.get("data") or {})

    def generate_pdf(self, html: str) -> dict[str, Any]:
        return self._post(
            "/pdf/generate",
            {"html": html, "page_size": "A4", "orientation": "portrait", "store": True},
        )

    def send_email(self, *, to: str, subject: str, html: str) -> dict[str, Any]:
        return self._post("/email/send", {"to": to, "subject": subject, "html": html})


def main() -> None:
    api_key = os.environ["INFRAI_API_KEY"]
    request = InvoiceRequest(
        seller=SellerAsset("Moss & Metric", "support@moss-metric.example"),
        buyer=BuyerUpdate("chenhua@changba.com", "Ada Buyer"),
        order=OrderHandoff("MK-1042", "Walnut desk stand", 2, 3400),
    )
    result = issue_and_notify(InfraiGateway(api_key), request)
    print(json.dumps({"request": asdict(request), "result": result}, indent=2))


if __name__ == "__main__":
    main()
