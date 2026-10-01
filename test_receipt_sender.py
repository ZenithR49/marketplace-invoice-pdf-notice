from typing import Any

from receipt_sender import BuyerUpdate, InvoiceRequest, OrderHandoff, SellerAsset, issue_and_notify


class RecordingGateway:
    def __init__(self) -> None:
        self.pdf_html = ""
        self.email: dict[str, str] = {}

    def generate_pdf(self, html: str) -> dict[str, Any]:
        self.pdf_html = html
        return {"job_id": "pdf-job-7"}

    def send_email(self, *, to: str, subject: str, html: str) -> dict[str, Any]:
        self.email = {"to": to, "subject": subject, "html": html}
        return {"message_id": "message-8"}


def test_issued_invoice_and_buyer_notice_share_the_same_order_record() -> None:
    request = InvoiceRequest(
        seller=SellerAsset("Moss & Metric", "support@example.com"),
        buyer=BuyerUpdate("ada@example.com", "Ada"),
        order=OrderHandoff("MK-1042", "Desk stand", 2, 3400),
    )
    gateway = RecordingGateway()

    result = issue_and_notify(gateway, request)

    assert "Invoice MK-1042" in gateway.pdf_html
    assert "$68.00" in gateway.email["html"]
    assert gateway.email["to"] == "ada@example.com"
    assert result == {"pdf": {"job_id": "pdf-job-7"}, "email": {"message_id": "message-8"}}
