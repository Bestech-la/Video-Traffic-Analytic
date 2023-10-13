import getConfig from 'next/config';

const { publicRuntimeConfig: config } = getConfig();
export const CLIENT_API_URL = `${config.NEXTAUTH_URL_INTERNAL}/api`;
export const CLIENT_API_V1_URL = `${config.API_ENDPOINT}/api/v1`;
export const CLIENT_SECRET_KEY = config.SECRET_KEY;
