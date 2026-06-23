import { defineConfig, Plugin } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import react from '@vitejs/plugin-react';
import { viteSSR } from 'vite-ssr/plugin';

// Import CSS-in-JS libraries
import styledComponents from 'styled-components';
import emotion from '@emotion/react';
import linaria from 'linaria';
import stitches from '@stitches/react';
import typestyle from 'typestyle';

// Define a plugin for CSS-in-JS support
const cssInJsPlugin: Plugin = () => {
  return {
    name: 'css-in-js',
    enforce: 'pre',
    transform(code, id) {
      // Implement transformations for CSS-in-JS libraries
      if (id.includes('styled-components')) {
        return code.replace('styled.div', 'styled.div.bind(this)');
      } else if (id.includes('@emotion/react')) {
        return code.replace('styled.div', 'emotion.styled.div.bind(this)');
      } else if (id.includes('linaria')) {
        return code.replace('styled.div', 'linaria.styled.div.bind(this)');
      } else if (id.includes('@stitches/react')) {
        return code.replace('styled.div', 'stitches.styled.div.bind(this)');
      } else if (id.includes('typestyle')) {
        return code;
      }
      return code;
    },
  };
};

// Define the Vite configuration
const config = defineConfig({
  plugins: [
    svelte(),
    react(),
    viteSSR(),
    cssInJsPlugin,
  ],
  ssr: {
    noExternal: ['styled-components', '@emotion/react', 'linaria', '@stitches/react', 'typestyle'],
    external: ['@astrojs/react'],
  },
  build: {
    ssr: true,
  },
});

// Export the configuration
export default config;