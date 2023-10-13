import { type HttpError } from '@refinedev/core';
import axios from 'axios';
import { SERVER_API_V1_URL } from '@src/lib/server-api-constants';

async function getAccessToken(): Promise<string | undefined> {
  try {
    const res = await fetch(`${SERVER_API_V1_URL}/auth/session`);
    const session = await res.json();
    return session?.user?.accessToken;
  } catch (error) {
    return undefined;
  }
}

const access: string | undefined = await getAccessToken();

const axiosInstance = access
  ? axios.create({
    headers: {
      Authorization: `Bearer ${access}`,
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
