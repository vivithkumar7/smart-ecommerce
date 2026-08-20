import { useNavigate } from "react-router-dom";

export default function CartSummary({
  cart,
}) {

  const navigate = useNavigate();

  return (
    <div className="cart-summary">

      <h2 className="summary-title">
        Order Summary
      </h2>


      <div className="summary-row">

        <span>
          Subtotal
        </span>

        <span>
          ₹{cart.subtotal}
        </span>

      </div>


      <div className="summary-row">

        <span>
          Tax (18%)
        </span>

        <span>
          ₹{cart.tax}
        </span>

      </div>


      <div className="summary-total">

        <span>
          Grand Total
        </span>

        <span>
          ₹{cart.grand_total}
        </span>

      </div>


      <button
        type="button"
        className="checkout-button"
        onClick={() => navigate("/checkout")}
      >
        Proceed to Checkout
      </button>

    </div>
  );
}