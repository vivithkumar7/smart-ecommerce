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

export const signupUser = async (email, password) => {
  const response = await api.post(
    "/auth/signup",
    {
      email,
      password,
    }
  );

  return response.data;
};