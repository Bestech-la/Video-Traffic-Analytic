import { type GetServerSideProps } from 'next';
import { getServerSession } from 'next-auth';
import { authOptions } from '../api/auth/[...nextauth]';
import { LoginComponent } from '@components/login';
import { getCsrfToken } from 'next-auth/react';

interface LoginProps {
  csrfToken: string;
}

export default function Login ({ csrfToken }: LoginProps) {
  return <LoginComponent csrfToken={csrfToken} />;
}

Login.noLayout = true;

export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getServerSession(context.req, context.res, authOptions);
  if (session != null) {
    return {
      props: {},
      redirect: {
        destination: '/',
        permanent: false,
      },
    };
  }

  return {
    props: {
      csrfToken: await getCsrfToken(context),
    },
  };
};
