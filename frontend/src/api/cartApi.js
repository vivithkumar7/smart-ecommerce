import api from "./axios";


export const getCart = async () => {
  const response = await api.get("/cart");

  return response.data;
};


export const addToCart = async (
  product_id,
  quantity = 1
) => {
  const response = await api.post("/cart/add", {
    product_id,
    quantity,
  });

  return response.data;
};


export const updateCart = async (
  product_id,
  quantity
) => {
  const response = await api.put("/cart/update", {
    product_id,
    quantity,
  });

  return response.data;
};


export const removeFromCart = async (
  product_id
) => {
  const response = await api.delete("/cart/remove", {
    data: {
      product_id,
    },
  });

  return response.data;
};


export const checkoutCart = async () => {
  const response = await api.post("/checkout");

  return response.data;
};