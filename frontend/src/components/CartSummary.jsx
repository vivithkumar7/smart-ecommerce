import { useNavigate } from "react-router-dom";

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value || 0);

export default function CartSummary({
  cart,
}) {

  const navigate = useNavigate();

  return (
    <aside className="cart-summary">
      <div className="summary-header">
        <h2 className="summary-title">Order Summary</h2>
        <span className="summary-badge">Secure checkout</span>
      </div>

      <div className="summary-row">
        <span>Subtotal</span>
        <span>{formatCurrency(cart.subtotal)}</span>
      </div>

      <div className="summary-row">
        <span>Tax (2%)</span>
        <span>{formatCurrency(cart.tax)}</span>
      </div>

      <div className="summary-row delivery-row">
        <span>Delivery</span>
        <span className="delivery-free">Free</span>
      </div>

      <div className="summary-total">
        <span>Grand Total</span>
        <span>{formatCurrency(cart.grand_total)}</span>
      </div>

      <button
        type="button"
        className="checkout-button"
        onClick={() => navigate("/checkout")}
      >
        Proceed to Checkout
      </button>

      <p className="summary-note">You are protected by secure payment checkout.</p>
    </aside>
  );
}