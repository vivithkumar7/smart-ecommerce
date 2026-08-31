import api from "./axios";

export const getOrders = async () => {
  const response = await api.get("/orders");
  return response.data;
};

export const requestReturn = async (orderId, payload) => {
  const response = await api.post(`/orders/${orderId}/return`, payload);
  return response.data;
};
