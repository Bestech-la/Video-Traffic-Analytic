import { AuthBindings, Refine } from "@refinedev/core";
import { dataProvider } from "../src/rest-data-provider";
import routerProvider, {
  UnsavedChangesNotifier,
} from "@refinedev/nextjs-router";
import { signIn, signOut, useSession, SessionProvider } from "next-auth/react";
import { useRouter } from "next/router";
import React from "react";

export const RefineWithoutLayout = (Story: React.FC) => {
  const { data, status } = useSession();
  const router = useRouter();
  const { to } = router.query;

  if (status === "loading") {
    return <span>loading...</span>;
  }

  const authProvider: AuthBindings = {
    login: async () => {
      signIn("auth0", {
        callbackUrl: to ? to.toString() : "/",
        redirect: true,
      });

      return {
        success: true,
      };
    },
    logout: async () => {
      signOut({
        redirect: true,
        callbackUrl: "/login",
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
      if (status === "unauthenticated") {
        return {
          authenticated: false,
          redirectTo: "/login",
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
      if (data?.user) {
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
    <Refine
      dataProvider={dataProvider("http://localhost:8000/api/v1")}
      routerProvider={routerProvider}
      authProvider={authProvider}
      resources={[
        {
          name: "user",
          list: "/user",
          show: "/user/:id",
        },
       
      ]}
    >
      <UnsavedChangesNotifier />
      <SessionProvider basePath={"http://localhost:3000/api/auth"}>
        <Story />
      </SessionProvider>
    </Refine>
  );
};
