import type { ESLintConfigArray } from 'eslint';
import plugin from 'eslint-plugin-react-hooks';

// Flat config for eslint-plugin-react-hooks
const flatConfig = [{
  plugins: {
    'react-hooks': plugin,
  },
  rules: plugin.configs.recommended.rules,
}];

export const configs = {
  'flat/recommended': flatConfig,
};

// Test the config
try {
  const eslint = require('eslint');
  const cli = eslint.CLIEngine;
  const configFile = 'eslint.config.js';
  const file = require('fs').createReadStream(configFile);
  const formatter = cli.getFormatter('compact');
  const engine = new cli(configFile);
  engine.executeOnFiles([__filename]).then((results) => {
    console.log(formatter(results));
  });
} catch (error) {
  console.error(error);
}