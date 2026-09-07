export function StarRating({ rating = 0, interactive = false, onChange }) {
  const roundedRating = Math.round(Number(rating) || 0);

  if (interactive) {
    return (
      <span className="star-rating star-rating-picker" role="radiogroup" aria-label="Choose a rating">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            className={star <= roundedRating ? "star filled" : "star"}
            role="radio"
            aria-checked={star === roundedRating}
            aria-label={`${star} ${star === 1 ? "star" : "stars"}`}
            onClick={() => onChange(star)}
          >
            ★
          </button>
        ))}
      </span>
    );
  }

  return (
    <span className="star-rating" aria-label={`${rating || 0} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span key={star} className={star <= roundedRating ? "star filled" : "star"}>★</span>
      ))}
    </span>
  );
}