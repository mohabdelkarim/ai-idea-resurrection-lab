import { NextApiRequest, NextApiResponse } from 'http';
import { NextPageContext } from 'next';
import { getServerSideProps } from 'next';
import { useRouter } from 'next/router';
import dynamic from 'next/dynamic';
import Head from 'next/head';
import Link from 'next/link';
import Script from 'next/script';
import Image from 'next/image';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { headers } from 'next/headers';

const HomePage = () => {
  return (
    <div>
      <h1>Home Page</h1>
    </div>
  );
};
export const getStaticProps = async () => {
  return {
    props: {},
  };
};
export const getStaticPaths = async () => {
  return {
    paths: [
      {
        params: { slug: '1' },
      },
    ],
    fallback: 'blocking',
  };
};
const PostPage = ({ slug }: { slug: string }) => {
  return (
    <div>
      <h1>Post {slug}</h1>
    </div>
  );
};
export const getServerSideProps = async (context: NextPageContext) => {
  const { req, res, params } = context;
  const { slug } = params;
  const response = await axios.get(`https://jsonplaceholder.typicode.com/posts/${slug}`);
  const data = response.data;
  return {
    props: {
      slug,
      data,
    },
  };
};
export default function App({ Component, pageProps }: any) {
  return (
    <div>
      <Head>
        <title>App</title>
      </Head>
      <Component {...pageProps} />
    </div>
  );
}