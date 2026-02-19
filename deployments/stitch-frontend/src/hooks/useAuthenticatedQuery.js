import { useQuery } from "@tanstack/react-query";
import { useAuth0 } from "@auth0/auth0-react";
import { createAuthenticatedFetcher } from "../auth/api";

export function useAuthenticatedQuery(queryOptions) {
  const { getAccessTokenSilently } = useAuth0();
  const fetcher = createAuthenticatedFetcher(getAccessTokenSilently);
  const { queryFn, ...rest } = queryOptions;
  return useQuery({ ...rest, queryFn: () => queryFn(fetcher) });
}
