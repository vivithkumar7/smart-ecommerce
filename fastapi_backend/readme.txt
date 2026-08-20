Smart E-Commerce
================

This repository contains a React/Vite storefront and a FastAPI backend. The
backend provides authentication, products, cart, orders, and Stripe checkout.

Project folders
---------------

  fastapi_backend/   FastAPI API, database models, seed data, and tests
  frontend/          React/Vite web application

Prerequisites
-------------

Install the following before starting:

* Python 3.10 or newer
* Node.js 18 or newer and npm
* MySQL 8 (or a compatible MySQL server)
* Optional: a Stripe test account and the Stripe CLI for real test payments

1. Create the database
----------------------

Create an empty MySQL database and user. For example, from MySQL Workbench or
the MySQL client:

  CREATE DATABASE smart_ecommerce;
  CREATE USER 'smart_user'@'localhost' IDENTIFIED BY 'change-this-password';
  GRANT ALL PRIVILEGES ON smart_ecommerce.* TO 'smart_user'@'localhost';
  FLUSH PRIVILEGES;

Use the actual username, password, host, port, and database name in the
DATABASE_URL below. The application creates its tables when it starts.

2. Configure the backend
------------------------

Open PowerShell in `fastapi_backend` and create a virtual environment:

  cd fastapi_backend
  py -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install --upgrade pip
  pip install -r requirements.txt

Create a file named `.env` inside `fastapi_backend` with these values:

  DATABASE_URL=mysql+pymysql://smart_user:change-this-password@localhost/smart_ecommerce
  SECRET_KEY=replace-with-a-long-random-value
  CHECKOUT_MODE=mock
  STRIPE_SECRET_KEY=sk_test_replace-me
  STRIPE_CURRENCY=usd
  STRIPE_SUCCESS_URL=http://localhost:5173/checkout?success=true
  STRIPE_CANCEL_URL=http://localhost:5173/checkout?cancelled=true
  STRIPE_WEBHOOK_SECRET=whsec_replace-me
  TAX_RATE=0.18

`SECRET_KEY` should be a long random value. Never commit `.env` or real Stripe
keys to source control. Mock checkout is recommended for initial local testing.

3. Start the backend
--------------------

Run this command from `fastapi_backend` with the virtual environment active:

  uvicorn app.main:app --reload

The API is available at http://127.0.0.1:8000. Confirm it is running by opening:

* http://127.0.0.1:8000/health
* http://127.0.0.1:8000/docs
* http://127.0.0.1:8000/redoc

4. Add sample products
---------------------

Keep the backend running, open a second PowerShell window, activate the same
environment, and run:

  cd fastapi_backend
  .\.venv\Scripts\Activate.ps1
  python seed.py

The seed script clears existing products and cart data, then inserts the sample
catalog. Run it only when resetting development catalog data is acceptable.

5. Start the frontend
---------------------

Open a third PowerShell window and run:

  cd frontend
  npm install
  npm run dev

Open the URL printed by Vite, normally http://localhost:5173. The frontend
calls the backend at `http://127.0.0.1:8000`; start the API first so products and
images load correctly.

6. Test the application
----------------------

In the browser:

1. Open the storefront and confirm the seeded products are visible.
2. Create a new account from the login page.
3. Sign in, add a product to the cart, and open checkout.
4. With `CHECKOUT_MODE=mock`, use the local checkout flow for frontend testing.
5. For Stripe testing, switch to `CHECKOUT_MODE=stripe` and configure the Stripe
   values described below.

Run the backend authentication smoke test from `fastapi_backend` while the API
is running in another terminal:

  python test_all_auth.py

The other `test_*.py` files exercise individual login and signup scenarios.

Run frontend checks from `frontend`:

  npm run lint
  npm run build

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

Useful API routes
-----------------

    GET  /health
    POST /auth/signup
    POST /auth/login
    GET  /products
    POST /cart/items
    GET  /cart
    POST /checkout
    GET  /orders/{order_id}
    POST /stripe/webhook

Authentication uses a JWT Bearer token. The frontend stores the token in
`localStorage` under `access_token` and sends it automatically with API calls.

Stripe test payments
--------------------

The Stripe secret must be a real test-mode key from the Stripe Dashboard. Set:

    CHECKOUT_MODE=stripe
    STRIPE_SECRET_KEY=sk_test_your_key
    STRIPE_WEBHOOK_SECRET=whsec_your_webhook_signing_secret

To forward Stripe events during local development, install the Stripe CLI and
run this in another terminal:

    stripe login
    stripe listen --forward-to localhost:8000/stripe/webhook

Copy the `whsec_...` value printed by the CLI into `.env`, then restart the
backend. Use Stripe's test card `4242 4242 4242 4242`, any future expiry date,
and any three-digit CVC when the hosted checkout page asks for payment details.

Checkout behavior
-----------------

`POST /checkout` requires an authenticated Bearer token and a non-empty cart.
It validates the cart, calculates subtotal plus `TAX_RATE`, snapshots the items
into an Order, creates a Stripe PaymentIntent and Checkout Session, records a
Payment, and clears the cart only after Stripe succeeds.

Stripe receives the amount in the smallest currency unit, the currency, and
`order_id` in PaymentIntent and Checkout Session metadata. The response includes
`order_id`, `payment_intent_id`, `checkout_session_id`, and `checkout_url`.
Redirect the browser to `checkout_url` to complete payment.

`POST /stripe/webhook` handles `checkout.session.completed`,
`payment_intent.succeeded`, and `payment_intent.payment_failed`. It verifies the
Stripe signature and updates the payment and order statuses. Do not treat a
client redirect as proof that payment succeeded.

Troubleshooting
---------------

* `Can't connect to MySQL`: verify MySQL is running and check every part of
  `DATABASE_URL`, including the database name and password.
* `ModuleNotFoundError`: activate `fastapi_backend\.venv` and rerun
  `pip install -r requirements.txt`.
* Products are empty: run `python seed.py` from `fastapi_backend`.
* Browser CORS errors: make sure Vite is using port 5173 or add the frontend
  origin to the CORS list in `app/main.py`.
* Images do not load: keep the backend running because product images are served
  from `http://127.0.0.1:8000/assets/`.
* Login fails for old development users: the current password hashing setup uses
  `pbkdf2_sha256`. Create a new user or clear and recreate development users;
  never delete production users without a backup and migration plan.