import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { addToCart } from "../api/cartApi";
import {
  getProductById,
  getSimilarProducts,
  getTrendingProducts,
} from "../api/productApi";
import { createReview, getProductReviews } from "../api/reviewApi";
import { StarRating } from "../components/StarRating";
import RecommendationSection from "../components/RecommendationSection";

import "../styles/product-details.css";


export default function ProductDetails() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [similarProducts, setSimilarProducts] = useState([]);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState("");
  const [reviewMessage, setReviewMessage] = useState("");
  const [reviewError, setReviewError] = useState("");
  const [submittingReview, setSubmittingReview] = useState(false);

  useEffect(() => {
    const loadProduct = async () => {
      try {
        setLoading(true);
        const [productData, reviewData, similarData, recommendedData] = await Promise.all([
          getProductById(productId),
          getProductReviews(productId),
          getSimilarProducts(productId),
          getTrendingProducts(),
        ]);
        setProduct(productData);
        setReviews(reviewData);
        setSimilarProducts(similarData);
        setRecommendedProducts(recommendedData);
      } catch (loadError) {
        setError(loadError.response?.data?.detail || "Unable to load this product.");
      } finally {
        setLoading(false);
      }
    };

    loadProduct();
  }, [productId]);

  const topReviews = useMemo(
    () => [...reviews].sort((first, second) => second.rating - first.rating).slice(0, 3),
    [reviews],
  );

  const handleAddToCart = async (productId = product.id) => {
    try {
      await addToCart(productId, 1);
      window.alert("Product added to cart!");
    } catch (addError) {
      window.alert(addError.response?.data?.detail || "Unable to add product.");
    }
  };

  const handleSubmitReview = async (event) => {
    event.preventDefault();

    if (!localStorage.getItem("access_token")) {
      navigate("/login");
      return;
    }

    setSubmittingReview(true);
    setReviewError("");
    setReviewMessage("");

    try {
      await createReview({
        product_id: product.id,
        rating: reviewRating,
        comment: reviewComment.trim() || null,
      });
      setReviewMessage("Review submitted and awaiting approval.");
      setReviewComment("");
      setShowReviewForm(false);
      const [updatedProduct, updatedReviews] = await Promise.all([
        getProductById(productId),
        getProductReviews(productId),
      ]);
      setProduct(updatedProduct);
      setReviews(updatedReviews);
    } catch (submitError) {
      setReviewError(
        submitError.response?.data?.detail || "Unable to submit your review.",
      );
    } finally {
      setSubmittingReview(false);
    }
  };

  if (loading) return <main className="product-details-page"><p className="product-details-state">Loading product...</p></main>;
  if (error || !product) return <main className="product-details-page"><p className="product-details-state error">{error || "Product not found."}</p></main>;

  return (
    <main className="product-details-page">
      <div className="product-details-container">
        <button type="button" className="back-button" onClick={() => navigate(-1)}>
          ← Back to collection
        </button>

        <section className="product-showcase">
          <div className="product-detail-image-wrap">
            {product.image_url ? (
              <img src={product.image_url} alt={product.name} className="product-detail-image" />
            ) : (
              <div className="product-detail-image empty">No image</div>
            )}
          </div>
          <div className="product-detail-copy">
            <span className="product-detail-category">{product.category}</span>
            <h1>{product.name}</h1>
            <div className="product-detail-rating">
              <StarRating rating={product.average_rating} />
              <strong>{product.average_rating ? product.average_rating.toFixed(1) : "New"}</strong>
              <span>{product.total_reviews} {product.total_reviews === 1 ? "review" : "reviews"}</span>
            </div>
            <button
              type="button"
              className="write-review-button"
              onClick={() => {
                if (!localStorage.getItem("access_token")) {
                  navigate("/login");
                  return;
                }
                setReviewError("");
                setReviewMessage("");
                setShowReviewForm((visible) => !visible);
              }}
            >
              {showReviewForm ? "Close review form" : "Write a review"}
            </button>
            <p className="product-detail-description">{product.description}</p>
            <div className="product-detail-buy-row">
              <strong className="product-detail-price">₹{Number(product.price).toLocaleString("en-IN")}</strong>
              <button type="button" className="product-detail-cart" disabled={product.stock <= 0} onClick={handleAddToCart}>
                {product.stock > 0 ? "Add to cart" : "Out of stock"}
              </button>
            </div>
          </div>
        </section>

        <RecommendationSection
          title="Similar Products"
          eyebrow="Complements this choice"
          products={similarProducts}
          onAddToCart={handleAddToCart}
        />

        <RecommendationSection
          title="You May Also Like"
          eyebrow="Popular with other shoppers"
          products={recommendedProducts.filter((item) => item.id !== product.id)}
          onAddToCart={handleAddToCart}
          showViewMore
        />

        {showReviewForm && (
          <form className="review-form" onSubmit={handleSubmitReview}>
            <div>
              <span className="section-kicker">Your experience</span>
              <h2>Write a review</h2>
              <p className="review-form-note">Reviews are available after a delivered purchase and are published after approval.</p>
            </div>
            <div className="review-rating-field">
              <span className="review-field-label">Rating</span>
              <StarRating rating={reviewRating} interactive onChange={setReviewRating} />
              <span className="review-rating-value">{reviewRating} / 5</span>
            </div>
            <label htmlFor="review-comment">Comment</label>
            <textarea
              id="review-comment"
              value={reviewComment}
              onChange={(event) => setReviewComment(event.target.value)}
              placeholder="What did you think of this product?"
              rows="4"
            />
            {reviewError && <p className="review-form-error">{reviewError}</p>}
            {reviewMessage && <p className="review-form-success">{reviewMessage}</p>}
            <button type="submit" className="product-detail-cart" disabled={submittingReview}>
              {submittingReview ? "Submitting..." : "Submit review"}
            </button>
          </form>
        )}

        <section className="reviews-section" aria-labelledby="reviews-heading">
          <div className="reviews-heading-row">
            <div>
              <span className="section-kicker">Customer notes</span>
              <h2 id="reviews-heading">Reviews & ratings</h2>
            </div>
            <div className="review-summary">
              <StarRating rating={product.average_rating} />
              <span>{product.total_reviews} total</span>
            </div>
          </div>

          {topReviews.length > 0 && (
            <div className="top-reviews">
              <div className="top-reviews-heading">
                <span className="section-kicker">Most loved</span>
                <h3>Top reviews</h3>
              </div>
              <div className="top-reviews-grid">
                {topReviews.map((review) => <ReviewCard key={review.id} review={review} featured />)}
              </div>
            </div>
          )}

          <div className="all-reviews-heading">
            <h3>All reviews</h3>
            <span>{reviews.length} published</span>
          </div>
          {reviews.length > 0 ? (
            <div className="reviews-list">
              {reviews.map((review) => <ReviewCard key={review.id} review={review} />)}
            </div>
          ) : (
            <p className="empty-reviews">No reviews yet. Be the first to share your experience.</p>
          )}
        </section>
      </div>
    </main>
  );
}


function ReviewCard({ review, featured = false }) {
  return (
    <article className={`review-card${featured ? " featured" : ""}`}>
      <div className="review-card-topline">
        <StarRating rating={review.rating} />
        <time dateTime={review.created_at}>{new Date(review.created_at).toLocaleDateString()}</time>
      </div>
      <p>{review.comment || "A lovely addition to everyday life."}</p>
      <span className="review-author">Verified customer #{review.user_id}</span>
    </article>
  );
}