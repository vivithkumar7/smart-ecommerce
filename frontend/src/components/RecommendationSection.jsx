import { useRef, useState } from "react";

import ProductCard from "./ProductCard";

import "../styles/recommendations.css";


export default function RecommendationSection({
  title,
  eyebrow,
  products,
  loading = false,
  onAddToCart,
  showViewMore = false,
}) {
  const recommendationGridRef = useRef(null);
  const [isExpanded, setIsExpanded] = useState(false);

  if (!loading && products.length === 0) return null;

  const handleViewMore = () => {
    setIsExpanded(true);
  };

  const slide = (direction) => {
    recommendationGridRef.current?.scrollBy({
      left: direction * recommendationGridRef.current.clientWidth,
      behavior: "smooth",
    });
  };

  return (
    <section className="recommendation-section" aria-label={title}>
      <div className="recommendation-heading">
        <div>
          <span className="recommendation-eyebrow">{eyebrow}</span>
          <h2>{title}</h2>
        </div>
        <div className="recommendation-actions">
          <span className="recommendation-count">{loading ? "Curating" : `${products.length} picks`}</span>
          {showViewMore && (
            <button type="button" className="recommendation-see-all" onClick={handleViewMore}>
              See all
            </button>
          )}
          <button type="button" className="recommendation-arrow" onClick={() => slide(-1)} aria-label={`Previous ${title}`}>
            &#8249;
          </button>
          <button type="button" className="recommendation-arrow" onClick={() => slide(1)} aria-label={`Next ${title}`}>
            &#8250;
          </button>
        </div>
      </div>
      {loading ? (
        <p className="recommendation-state">Finding your next favorite...</p>
      ) : (
        <div className="product-grid recommendation-grid" ref={recommendationGridRef}>
          {products.slice(0, isExpanded || !showViewMore ? 8 : 4).map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} />
          ))}
          {showViewMore && !isExpanded && products.length > 4 && (
            <button type="button" className="recommendation-more" onClick={handleViewMore}>
              <span>View more</span>
              <strong aria-hidden="true">→</strong>
            </button>
          )}
        </div>
      )}
    </section>
  );
}