import { type CrudFilters } from '@refinedev/core';
import { mapOperator } from './mapOperator';

export const generateFilter = (filters?: CrudFilters) => {
  const queryFilters: Record<string, string> = {};

  if (filters != null) {
    filters.map((filter) => {
      if (filter.operator === 'or' || filter.operator === 'and') {
        throw new Error(
          `[@refinedev/simple-rest]: \`operator: ${filter.operator}\` is not supported. You can create custom data provider. https://refine.dev/docs/api-reference/core/providers/data-provider/#creating-a-data-provider`,
        );
      }

      if ('field' in filter) {
        const { field, operator, value } = filter;

        if (field === 'q') {
          queryFilters[field] = value;
          return;
        }

        const mappedOperator = mapOperator(operator);
        queryFilters[`${field}${mappedOperator}`] = value;
      }
    });
  }

  return queryFilters;
};
