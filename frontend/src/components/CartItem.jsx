const formatCurrency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value || 0);

export default function CartItem({
  item,
  onUpdate,
  onRemove,
}) {

  return (
    <div className="cart-item">

      <div className="cart-item-info">
        <span className="cart-item-tag">Premium pick</span>
        <h3 className="cart-item-name">
          {item.product_name}
        </h3>

        <div className="cart-item-price">
          {formatCurrency(item.unit_price)} each
        </div>
      </div>

      <div className="quantity-control">
        <button
          className="quantity-button"
          onClick={() =>
            onUpdate(
              item.product_id,
              item.quantity - 1
            )
          }
          type="button"
        >
          −
        </button>

        <span className="quantity-value">
          {item.quantity}
        </span>

        <button
          className="quantity-button"
          onClick={() =>
            onUpdate(
              item.product_id,
              item.quantity + 1
            )
          }
          type="button"
        >
          +
        </button>
      </div>

      <div className="cart-item-total">
        {formatCurrency(item.item_total)}
      </div>

      <button
        className="remove-button"
        onClick={() =>
          onRemove(item.product_id)
        }
        type="button"
      >
        Remove
      </button>
    </div>
  );
}