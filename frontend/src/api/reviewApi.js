import api from "./axios";


export const getProductReviews = async (productId) => {
  const response = await api.get(`/products/${productId}/reviews`);
  return response.data;
};


export const createReview = async (reviewData) => {
  const response = await api.post("/reviews", reviewData);
  return response.data;
};