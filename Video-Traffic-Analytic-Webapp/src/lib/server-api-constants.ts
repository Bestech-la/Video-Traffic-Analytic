import getConfig from 'next/config';

const { serverRuntimeConfig: config } = getConfig();

export const SERVER_API_URL = `${config.NEXTAUTH_URL_INTERNAL}/api`;
export const SERVER_API_V1_URL = `${config.API_ENDPOINT}/api/v1`;
export const SERVER_SECRET_KEY = config.SECRET_KEY;
