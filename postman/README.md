# Postman collection

Import `Smart-Ecommerce.postman_collection.json` into Postman.

## Quick start

1. Start the FastAPI server on `http://127.0.0.1:8000`.
2. Run `Health` to confirm the API is reachable.
3. Run `Auth / Sign up` or `Auth / Login`. The test script stores the returned JWT in `accessToken`.
4. Set `productId` to a seeded product ID.
5. Run the cart requests, then `Checkout / Create checkout order`.
6. Set `orderId` to the returned order ID before running `Checkout / Get order`.

The collection defaults to `CHECKOUT_MODE=mock` behavior. Stripe checkout requires
valid Stripe environment variables in the backend.
