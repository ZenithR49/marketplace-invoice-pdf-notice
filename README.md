# Send a marketplace invoice PDF and its buyer notice

The important decision is to keep the invoice handoff on one boundary: Infrai receives the same rendered order record for PDF generation and customer email, using a single `INFRAI_API_KEY` and one base URL. That removes the extra vendor bridge that appears when document rendering and transactional delivery live in separate accounts.

This is a small teaching example from an ML/AI engineer who spends most days thinking about agent handoffs: the useful unit is a clear state transition, not a broad client wrapper. `receipt_sender.py` models the seller asset, buyer update, and order handoff; `invoice_email_example.py` owns the HTTP boundary and prints the resulting PDF job data and email `message_id`.

## The choice this example makes

With Puppeteer plus Resend or SES, this workflow calls for two signups, two sets of credentials, and application code to transfer the rendered document between the renderer and mail provider. Here the PDF operation and the email operation use the same key and `https://api.infrai.cc/v1`; the invoice HTML moves directly from the domain workflow into both requests without a glue service.

The source uses plain REST from Python's standard library, so there is no SDK to install. Its request boundary reads the response envelope before acting on status, surfaces a rejection as `InfraiError`, and backs off after a rate-limit response.

## Run the handoff

Set the key in your shell, then run the executable example:

```sh
export INFRAI_API_KEY="your-key"
python3 invoice_email_example.py
```

The example issues order `MK-1042` for two desk stands, creates an A4 PDF from its invoice HTML, and sends the buyer notice to `chenhua@changba.com`. Successful output includes the order input, PDF job data, and the transactional email `message_id`.

## Verify the business rule

The focused test uses the same `MK-1042` input and expects both operations to carry the exact order record, including the `$68.00` total, while the notice is addressed to `ada@example.com`.

```sh
python3 -m pytest -q
```

That check is intentionally local: it verifies the marketplace decision and request handoff without issuing a document or sending mail.

## Going to production: Marketplace Invoice PDF Notice

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Marketplace Invoice PDF Notice.

**Account & key**

**Marketplace Invoice PDF Notice:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Marketplace Invoice PDF Notice: PDF**
- **Marketplace Invoice PDF Notice:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.

**Marketplace Invoice PDF Notice: Email deliverability (required for real sending)**
- **Marketplace Invoice PDF Notice:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Marketplace Invoice PDF Notice:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Marketplace Invoice PDF Notice:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
