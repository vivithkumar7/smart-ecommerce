export default function CartItem({
  item,
  onUpdate,
  onRemove,
}) {

  return (
    <div className="cart-item">

      <div className="cart-item-info">

        <h3 className="cart-item-name">
          {item.product_name}
        </h3>

        <div className="cart-item-price">
          ₹{item.unit_price} each
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
        >
          +
        </button>

      </div>


      <div className="cart-item-total">
        ₹{item.item_total}
      </div>


      <button
        className="remove-button"
        onClick={() =>
          onRemove(item.product_id)
        }
      >
        Remove
      </button>

    </div>
  );
}