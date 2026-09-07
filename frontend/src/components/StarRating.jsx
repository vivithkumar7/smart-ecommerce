export function StarRating({ rating = 0 }) {
  const roundedRating = Math.round(Number(rating) || 0);

  return (
    <span className="star-rating" aria-label={`${rating || 0} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span key={star} className={star <= roundedRating ? "star filled" : "star"}>★</span>
      ))}
    </span>
  );
}