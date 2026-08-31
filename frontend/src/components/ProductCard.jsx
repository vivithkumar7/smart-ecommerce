export default function ProductCard({
  product,
  onAddToCart,
}) {

  const {
    id,
    name,
    description,
    category,
    price,
    popularity,
    stock,
    image_url,
  } = product;


  return (
    <div className="product-card">
      <div className="product-image-container">
        {image_url ? (
          <img
            src={image_url}
            alt={name}
            className="product-image"
          />
        ) : (
          <div className="no-image">
            No Image
          </div>
        )}

        <div className="product-hero-overlay" />

        <div className="product-topline">
          <span className={stock > 0 ? "stock-badge" : "stock-badge out-stock-badge"}>
            {stock > 0 ? `${stock} in stock` : "Out of stock"}
          </span>
          <span className="product-badge">Premium</span>
        </div>
      </div>

      <div className="product-content">
        <div className="product-headline">
          <span className="product-category">{category}</span>
          <span className="product-rating">
            <span className="rating-star">★</span>
            {popularity}
          </span>
        </div>

        <h3 className="product-name">{name}</h3>
        <p className="product-description">{description}</p>

        <div className="product-price-row">
          <div className="product-price">₹{Number(price).toLocaleString("en-IN")}</div>
          <div className="product-shipping">Free shipping</div>
        </div>

        <button
          className="add-cart-button"
          disabled={stock <= 0}
          onClick={() => onAddToCart(id)}
        >
          {stock > 0 ? "Add to Cart" : "Out of Stock"}
        </button>
      </div>
    </div>
  );
}