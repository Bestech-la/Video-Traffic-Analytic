import { type NextApiHandler } from 'next';
import NextAuth, { type NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import Cors from 'nextjs-cors';

interface User {
  id: string;
  name: string;
  email: string;
  image: string | null;
}

export const authOptions: NextAuthOptions = {
  pages: {
    signIn: '/login',
  },
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: 'Username', type: 'text' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize (credentials) {
        const res = await fetch('http://localhost:8000/api/v1/auth/login/', {
          method: 'POST',
          body: JSON.stringify(credentials),
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await res.json();
        if (res.ok && data?.access_token) {
          const user: User = {
            name: data.user.username,
            email: data.user.email,
            id: data.user.userId,
            image: null,
          };
          return { ...user, accessToken: data.access_token };
        }
        return null;
      },
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  secret: 'bMFZFfDdzpgqlcQZklCdPldjAWAiMxfNZCIHvTtfHhSLyukxLz%',

  callbacks: {
    async session ({ session, token }) {
      if (token?.user) {
        session.user = token.user;
      }
      return { ...session, accessToken: token.accessToken };
    },
    async jwt ({ token, user, account }) {
      if (user) {
        token.user = user;
        token.accessToken = account?.accessToken;
      }
      return token;
    },
    async signIn ({ user }) {
      return !!user;
    },
    async redirect ({ baseUrl }) {
      return `${baseUrl}`;
    },
  },
};

const handler: NextApiHandler = async (req, res) => {
  await Cors(req, res);

  return NextAuth(req, res, authOptions);
};

export default handler;
