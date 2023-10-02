/* eslint-disable @typescript-eslint/ban-types */
import React, { useEffect } from 'react';
import { type AppProps } from 'next/app';
import type { NextPage } from 'next';
import { Refine, type AuthBindings } from '@refinedev/core';
import { RefineKbar, RefineKbarProvider } from '@refinedev/kbar';
import { SessionProvider, useSession, signOut, signIn } from 'next-auth/react';
import { useRouter } from 'next/router';
import '@styles/globals.css';
import routerProvider, {
  UnsavedChangesNotifier,
} from '@refinedev/nextjs-router';
import { dataProvider } from 'src/rest-data-provider';
import 'moment/locale/lo';

const API_URL = 'http://127.0.0.1:8000/api/v1';
import 'react-toastify/dist/ReactToastify.css';

export type NextPageWithLayout<P = {}, IP = P> = NextPage<P, IP> & {
  noLayout?: boolean;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

const App = (props: React.PropsWithChildren) => {
  useEffect(() => {
    import('preline');
  }, []);

  const { data, status } = useSession();

  const router = useRouter();
  const { to } = router.query;

  if (status === 'loading') {
    return <span>loading...</span>;
  }

  const authProvider: AuthBindings = {
    login: async () => {
      signIn('auth0', {
        callbackUrl: to ? to.toString() : '/',
        redirect: true,
      });

      return {
        success: true,
      };
    },
    logout: async () => {
      signOut({
        redirect: true,
        callbackUrl: '/login',
      });

      return {
        success: true,
      };
    },
    onError: async (error) => {
      console.error(error);
      return {
        error,
      };
    },
    check: async () => {
      if (status === 'unauthenticated') {
        return {
          authenticated: false,
          redirectTo: '/login',
        };
      }

      return {
        authenticated: true,
      };
    },
    getPermissions: async () => {
      return null;
    },
    getIdentity: async () => {
      if (data?.user != null) {
        const { user } = data;
        return {
          name: user.name,
          avatar: user.image,
        };
      }
      return null;
    },
  };

  return (
    <RefineKbarProvider>
      <Refine
        routerProvider={routerProvider}
        dataProvider={dataProvider(API_URL)}
        authProvider={authProvider}
        resources={[
          {
            name: 'infraction_tracker',
            list: '/infraction_tracker',
          },
        ]}
        options={{
          syncWithLocation: true,
          warnWhenUnsavedChanges: true,
        }}
      >
        {props.children}

        <RefineKbar />
        <UnsavedChangesNotifier />
      </Refine>
    </RefineKbarProvider>
  );
};

function MyApp ({
  Component,
  pageProps: { session, ...pageProps },
}: AppPropsWithLayout): JSX.Element {
  const renderComponent = () => {
    if (Component.noLayout) {
      return <Component {...pageProps} />;
    }

    return <Component {...pageProps} />;
  };

  return (
    <SessionProvider
      session={session}
      basePath={'http://localhost:3000/api/auth'}
    >
      <App>{renderComponent()}</App>
    </SessionProvider>
  );
}

export default MyApp;
