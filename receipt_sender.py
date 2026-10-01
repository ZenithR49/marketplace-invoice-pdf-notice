"""Small domain module for handing an issued marketplace invoice to a buyer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class SellerAsset:
    store_name: str
    support_email: str


@dataclass(frozen=True)
class BuyerUpdate:
    email: str
    display_name: str


@dataclass(frozen=True)
class OrderHandoff:
    order_number: str
    item_name: str
    quantity: int
    unit_price_cents: int


@dataclass(frozen=True)
class InvoiceRequest:
    seller: SellerAsset
    buyer: BuyerUpdate
    order: OrderHandoff


class InvoiceGateway(Protocol):
    def generate_pdf(self, html: str) -> dict[str, Any]:
        return {}

    def send_email(self, *, to: str, subject: str, html: str) -> dict[str, Any]:
        return {}


def invoice_html(request: InvoiceRequest) -> str:
    """Render the buyer-facing record once so both capability calls share it."""
    if request.order.quantity < 1:
        raise ValueError("quantity must be at least one")
    if request.order.unit_price_cents < 0:
        raise ValueError("unit_price_cents cannot be negative")

    total_cents = request.order.quantity * request.order.unit_price_cents
    return f"""<html><body>
<h1>Invoice {request.order.order_number}</h1>
<p>From: {request.seller.store_name}</p>
<p>Bill to: {request.buyer.display_name}</p>
<table><tr><th>Item</th><th>Qty</th><th>Total</th></tr>
<tr><td>{request.order.item_name}</td><td>{request.order.quantity}</td>
<td>${total_cents / 100:.2f}</td></tr></table>
<p>Questions: {request.seller.support_email}</p>
</body></html>"""


def issue_and_notify(gateway: InvoiceGateway, request: InvoiceRequest) -> dict[str, Any]:
    """Issue before notifying, keeping the business transition explicit."""
    html = invoice_html(request)
    pdf = gateway.generate_pdf(html)
    email = gateway.send_email(
        to=request.buyer.email,
        subject=f"Your invoice for order {request.order.order_number}",
        html=html,
    )
    return {"pdf": pdf, "email": email}
