import api from "./axios";

export const getProducts = async (filters = {}) => {
  const params = {};

  if (filters.category) {
    params.category = filters.category;
  }

  if (filters.min_price !== "") {
    params.min_price = filters.min_price;
  }

  if (filters.max_price !== "") {
    params.max_price = filters.max_price;
  }

  if (filters.min_popularity !== "") {
    params.min_popularity = filters.min_popularity;
  }

  if (filters.in_stock) {
    params.in_stock = true;
  }

  const response = await api.get("/products", {
    params,
  });

  return response.data;
};


export const getProductById = async (id) => {
  const response = await api.get(`/products/${id}`);

  return response.data;
};


export const getProductsByCategory = async (category) => {
  const response = await api.get(
    `/products/category/${category}`
  );

  return response.data;
};