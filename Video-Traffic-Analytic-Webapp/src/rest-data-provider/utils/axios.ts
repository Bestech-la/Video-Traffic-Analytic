import { type HttpError } from '@refinedev/core';
import axios from 'axios';

async function getAccessToken () {
  const res = await fetch('http://localhost:3000/api/auth/session');
  const session = await res.json();
  return session?.user?.accessToken;
}

const access_token = await getAccessToken ();

const axiosInstance = access_token
  ? axios.create({
    headers: {
      Authorization: `Bearer ${access_token}`,
    },
  })
  : axios.create();

axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const customError: HttpError = {
      ...error,
      message: error.response?.data?.message,
      statusCode: error.response?.status,
    };

    return await Promise.reject(customError);
  },
);

export { axiosInstance };
