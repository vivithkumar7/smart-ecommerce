Smart E-Commerce Checkout API

Setup
-----
Install dependencies from requirements.txt, then configure these environment variables:

The Stripe secret must be a real test-mode key from the Stripe Dashboard. Do not
commit it to source control.

DATABASE_URL=mysql+pymysql://user:password@localhost/database
SECRET_KEY=replace-with-a-long-random-value
STRIPE_SECRET_KEY=sk_test_replace-me
STRIPE_CURRENCY=usd
STRIPE_SUCCESS_URL=http://localhost:5173/checkout?success=true
STRIPE_CANCEL_URL=http://localhost:5173/checkout?cancelled=true
STRIPE_WEBHOOK_SECRET=whsec_replace-me
TAX_RATE=0.18

Run the API from fastapi_backend:

uvicorn app.main:app --reload

Checkout
--------
POST /checkout

Requires an authenticated Bearer token and a non-empty cart. The endpoint validates
the cart, calculates subtotal plus TAX_RATE, snapshots the items into an Order,
creates a Stripe PaymentIntent and Checkout Session, records a Payment, and clears
the cart only after Stripe succeeds.

Stripe receives amount in the smallest currency unit, currency, and order_id in
both the PaymentIntent and Checkout Session metadata:

{
  "amount": 5999,
  "currency": "usd",
  "metadata": {"order_id": "42"}
}

The Checkout Session also contains the invoice amount and currency in metadata,
while its line_items produce the hosted Stripe invoice. The Order stores both
the item snapshots and a read-only products relationship.

The response includes order_id, payment_intent_id, checkout_session_id, and
checkout_url. Redirect the browser to checkout_url to complete payment.

Order and payment tracking
--------------------------
GET /orders/{order_id}

Returns the authenticated user's order, its snapshotted items, and payment records.
Order status values are pending, paid, shipped, delivered, and cancelled.

Production payment updates
--------------------------
POST /stripe/webhook receives checkout.session.completed,
payment_intent.succeeded, and payment_intent.payment_failed.
Configure a Stripe webhook to call this endpoint.
The webhook verifies Stripe-Signature, finds the order using metadata.order_id,
and updates Payment.status, Payment.transaction_id, and Order.payment_status.
Do not trust client redirects as proof of payment.

When CHECKOUT_MODE=mock, the webhook returns 200 with mode=mock for local
frontend testing and does not process Stripe events. For real Stripe payments,
set CHECKOUT_MODE=stripe and replace STRIPE_WEBHOOK_SECRET with the signing
secret from Stripe Dashboard or Stripe CLI.

API docs are available at /docs and /redoc.