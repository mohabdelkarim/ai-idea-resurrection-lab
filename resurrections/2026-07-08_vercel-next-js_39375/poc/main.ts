import * as path from 'path';
import * as fs from 'fs';
import { Configuration } from 'webpack';

const config: Configuration = {
  // ... other configurations ...
  resolve: {
    // ... other resolve configurations ...
    exports: {
      // Add this line to handle the 'exports' field in package.json
      import: ['.mjs', '.js'],
      require: ['.js'],
    },
  },
};

// Create a webpack compiler instance
const webpack = require('webpack');
const compiler = webpack(config);

// Compile the code
compiler.run((err, stats) => {
  if (err) {
    console.error(err);
    return;
  }

  if (stats.hasErrors()) {
    console.error(stats.toString('errors-only'));
    return;
  }

  console.log('Compilation successful');
});

// Handle errors
process.on('unhandledRejection', (reason) => {
  console.error('Unhandled rejection:', reason);
  process.exit(1);
});

process.on('uncaughtException', (err) => {
  console.error('Uncaught exception:', err);
  process.exit(1);
});