/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/ban-ts-comment */
// "axios" package needs to be installed
import { type AxiosInstance } from 'axios';
// "stringify" function is re-exported from "query-string" package by "@refinedev/simple-rest"
import { stringify } from '@refinedev/simple-rest';
import { type DataProvider } from '@refinedev/core';
import { axiosInstance, generateSort, generateFilter } from './utils';
export const dataProvider = (
  apiUrl: string,
  httpClient: AxiosInstance = axiosInstance,
): Omit<
Required<DataProvider>,
'createMany' | 'updateMany' | 'deleteMany'
> => ({
  getList: async ({ resource, pagination, filters, sorters }) => {
    const url = `${apiUrl}/${resource}`;

    const { current = 1, pageSize = 10, mode = 'server' } = pagination ?? {};
    const queryFilters = generateFilter(filters);

    const query: {
      page_size?: number
      page?: number
      _sort?: string
      _order?: string
    } = {};

    if (mode === 'server') {
      query.page = current;
      query.page_size = pageSize;
    }

    const generatedSort = generateSort(sorters);
    if (generatedSort != null) {
      const { _sort, _order } = generatedSort;
      query._sort = _sort.join(',');
      query._order = _order.join(',');
    }

    const { data, headers } = await httpClient.get(
      `${url}?${stringify(query)}&${stringify(queryFilters)}`,
    );
    const total = data.count;
    return {
      data: data.results,
      total,
    };
  },

  getMany: async ({ resource, ids }) => {
    const { data } = await httpClient.get(
      `${apiUrl}/${resource}?${stringify({ id: ids })}`,
    );

    return {
      data: data.results,
    };
  },

  create: async ({ resource, variables, meta }) => {
    const headers = meta?.headers ?? {};
    const url = `${apiUrl}/${resource}`;
    const formData = new FormData();
    const is_form_data = headers['content-type'] === 'multipart/form-data';
    if (is_form_data) {
      for (const key in variables) {
        // @ts-expect-error
        const file_or_text = variables[key] instanceof FileList ? variables[key].item(0) : variables[key];
        formData.append(key, file_or_text);
      }
    }
    const form_data_or_json = is_form_data ? formData : variables;
    const { data } = await httpClient.post(url, form_data_or_json, { headers });
    return {
      data,
    };
  },

  update: async ({ resource, id, variables, meta }) => {
    const headers = meta?.headers ?? {};
    const url = `${apiUrl}/${resource}/${id}`;
    const formData = new FormData();
    const is_form_data = headers['content-type'] === 'multipart/form-data';
    if (is_form_data) {
      for (const key in variables) {
        // @ts-expect-error
        const file_or_text = variables[key] instanceof FileList ? variables[key].item(0) : variables[key];
        formData.append(key, file_or_text);
      }
    }
    const form_data_or_json = is_form_data ? formData : variables;
    const { data } = await httpClient.patch(url, form_data_or_json, { headers });
    return {
      data,
    };
  },

  getOne: async ({ resource, id }) => {
    const url = `${apiUrl}/${resource}/${id}`;
    const { data, headers } = await httpClient.get(url);
    return {
      data,
    };
  },

  deleteOne: async ({ resource, id, variables }) => {
    const url = `${apiUrl}/${resource}/${id}`;

    const { data } = await httpClient.delete(url, {
      data: variables,
    });

    return {
      data,
    };
  },

  getApiUrl: () => {
    return apiUrl;
  },

  custom: async ({
    url,
    method,
    filters,
    sorters,
    payload,
    query,
    headers,
  }) => {
    let requestUrl = `${url}?`;

    if (sorters != null) {
      const generatedSort = generateSort(sorters);
      if (generatedSort != null) {
        const { _sort, _order } = generatedSort;
        const sortQuery = {
          _sort: _sort.join(','),
          _order: _order.join(','),
        };
        requestUrl = `${requestUrl}&${stringify(sortQuery)}`;
      }
    }

    if (filters != null) {
      const filterQuery = generateFilter(filters);
      requestUrl = `${requestUrl}&${stringify(filterQuery)}`;
    }

    if (query) {
      requestUrl = `${requestUrl}&${stringify(query)}`;
    }

    if (headers != null) {
      httpClient.defaults.headers = {
        ...httpClient.defaults.headers,
        ...headers,
      };
    }

    let axiosResponse;
    switch (method) {
    case 'put':
    case 'post':
    case 'patch':
      axiosResponse = await httpClient[method](`${apiUrl}/${url}`, payload);
      break;
    case 'delete':
      axiosResponse = await httpClient.delete(`${apiUrl}/${url}`, {
        data: payload,
      });
      break;
    default:
      axiosResponse = await httpClient.get(requestUrl);
      break;
    }

    const { data } = axiosResponse;

    return await Promise.resolve({ data });
  },
});
