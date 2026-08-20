import api from "./axios";

export const loginUser = async (email, password) => {
  const response = await api.post(
    "/auth/login",
    {
      username: email,
      password: password,
    }
  );

  return response.data;
};