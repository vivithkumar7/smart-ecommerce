import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSearchParams } from "react-router-dom";

import { checkoutCart, getCart } from "../api/cartApi";

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value || 0);

const paymentOptions = [
  { id: "cod", label: "Cash on Delivery" },
  { id: "card", label: "Card" },
  { id: "credit-card", label: "Credit Card" },
  { id: "gpay", label: "GPay" },
  { id: "paytm", label: "Paytm" },
];

export default function Checkout() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [cart, setCart] = useState(null);
  const [cartLoading, setCartLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState("card");
  const paymentSucceeded = searchParams.get("success") === "true";
  const paymentCancelled = searchParams.get("cancelled") === "true";
  const orderId = searchParams.get("order_id");

  useEffect(() => {
    getCart()
      .then(setCart)
      .catch(() => setCart(null))
      .finally(() => setCartLoading(false));
  }, []);

  const handleCheckout = async () => {
    try {
      setLoading(true);
      const payment = await checkoutCart(selectedPayment);

      if (selectedPayment === "cod") {
        navigate(`/checkout?success=true&order_id=${payment.order_id}`);
        return;
      }

      if (payment.checkout_url) {
        window.location.assign(payment.checkout_url);
        return;
      }
      navigate(`/checkout?success=true&order_id=${payment.order_id}`);
    } catch (error) {
      alert(error.response?.data?.detail || "Unable to confirm order.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout-page">
      <div className="checkout-container">
        <div className="checkout-heading">
          <div>
            <span className="checkout-kicker">Secure payment</span>
            <h1>Review & checkout</h1>
            <p>Check your invoice before continuing to secure payment.</p>
          </div>
          <div className="checkout-step">Step <strong>2</strong> of 2</div>
        </div>

        {paymentSucceeded ? (
          <div className="order-success">
            <div className="success-tick" aria-hidden="true">
              <span>✓</span>
            </div>
            <span className="success-kicker">Payment confirmed</span>
            <h2>Your order is successful!</h2>
            <p className="success-copy">Thank you for your purchase. Your payment has been received and your order is now being processed.</p>
            {orderId && <div className="success-order-number">Order <strong>#{orderId}</strong></div>}
            <div className="success-divider" />
            <p className="success-note">A confirmation will be sent after your order is prepared.</p>
            <button className="success-button" type="button" onClick={() => navigate("/")}>Continue Shopping <span>→</span></button>
          </div>
        ) : paymentCancelled ? (
          <div className="checkout-status checkout-status-cancelled">
            <span className="status-mark">!</span>
            <div>
              <h2>Payment cancelled</h2>
              <p>Your cart is still available whenever you are ready.</p>
            </div>
            <button type="button" onClick={() => navigate("/cart")}>Return to Cart</button>
          </div>
        ) : (
          <div className="checkout-layout">
            <section className="invoice-card" aria-labelledby="invoice-title">
              <div className="invoice-topline">
                <div>
                  <span className="invoice-label">Invoice</span>
                  <h2 id="invoice-title">Order summary</h2>
                </div>
                <button className="print-button" type="button" onClick={() => window.print()}>Print</button>
              </div>

              {cartLoading ? (
                <div className="invoice-loading">Loading your items...</div>
              ) : cart?.items?.length ? (
                <>
                  <div className="invoice-items">
                    {cart.items.map((item) => (
                      <div className="invoice-item" key={item.product_id}>
                        <div>
                          <strong>{item.product_name}</strong>
                          <span>{item.quantity} × {formatCurrency(item.unit_price)}</span>
                        </div>
                        <strong>{formatCurrency(item.item_total)}</strong>
                      </div>
                    ))}
                  </div>
                  <div className="invoice-totals">
                    <div><span>Subtotal</span><strong>{formatCurrency(cart.subtotal)}</strong></div>
                    <div><span>Tax (2%)</span><strong>{formatCurrency(cart.tax)}</strong></div>
                    <div className="invoice-grand-total"><span>Total due</span><strong>{formatCurrency(cart.grand_total)}</strong></div>
                  </div>
                </>
              ) : (
                <div className="invoice-empty">Your cart is empty. Add products before checkout.</div>
              )}
            </section>

            <aside className="payment-card">
              <div className="payment-card-topline">
                <div className="payment-card-icon">₹</div>
                <span className="session-badge">Stripe session</span>
              </div>
              <span className="invoice-label">Ready when you are</span>
              <h2>Complete your payment</h2>
              <p>You will be redirected to Stripe's secure checkout to finish this order.</p>
              <div className="payment-methods" aria-label="Accepted payment methods">
                {paymentOptions.map((method) => (
                  <button
                    key={method.id}
                    type="button"
                    className={`payment-option ${selectedPayment === method.id ? "selected" : ""}`}
                    onClick={() => setSelectedPayment(method.id)}
                  >
                    {method.label}
                  </button>
                ))}
              </div>

              <div className="payment-amount">
                <span>Selected method</span>
                <strong>{paymentOptions.find((m) => m.id === selectedPayment)?.label}</strong>
              </div>
              <div className="payment-amount">
                <span>Total due</span>
                <strong>{formatCurrency(cart?.grand_total)}</strong>
              </div>
              <button
                type="button"
                className="checkout-confirm-button"
                onClick={handleCheckout}
                disabled={loading || cartLoading || !cart?.items?.length}
              >
                {loading
                  ? "Opening Stripe..."
                  : selectedPayment === "cod"
                    ? "Place order"
                    : "Continue to payment"}
              </button>
              <div className="payment-steps">
                <div><span>1</span><b>Review</b></div>
                <i />
                <div><span>2</span><b>Pay</b></div>
                <i />
                <div><span>3</span><b>Done</b></div>
              </div>
              <div className="secure-note">Encrypted checkout · Stripe protected</div>
            </aside>
          </div>
        )}
      </div>
    </div>
  );
}
