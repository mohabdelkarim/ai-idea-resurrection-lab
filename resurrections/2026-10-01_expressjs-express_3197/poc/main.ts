import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import http from 'http';

// Extend Express's StaticOptions to include the new `immutable` flag.
interface ExtendedStaticOptions extends express.StaticOptions {
  immutable?: boolean; // when true, adds `immutable` to Cache-Control header
}

/**
 * Wrapper around express.static that respects the `immutable` option.
 * It injects a custom `setHeaders` callback to modify Cache‑Control.
 */
function staticWithImmutable(root: string, opts: ExtendedStaticOptions = {}): express.Handler {
  // Preserve any user‑provided setHeaders function.
  const userSetHeaders = opts.setHeaders;

  // Create a new options object to avoid mutating the original.
  const options: express.StaticOptions = { ...opts };

  // Override setHeaders to add immutable handling.
  options.setHeaders = (res: Response, filePath: string, stat: any) => {
    try {
      // If the user supplied a setHeaders, call it first.
      if (typeof userSetHeaders === 'function') {
        userSetHeaders(res, filePath, stat);
      }

      // Express's static middleware already sets Cache‑Control based on maxAge.
      // We append `immutable` when the flag is true.
      if (opts.immutable) {
        const existing = res.getHeader('Cache-Control');
        const immutableToken = 'immutable';
        if (typeof existing === 'string') {
          // Avoid duplicate immutable token.
          if (!existing.includes(immutableToken)) {
            res.setHeader('Cache-Control', `${existing}, ${immutableToken}`);
          }
        } else {
          // Fallback if no Cache‑Control was set.
          res.setHeader('Cache-Control', immutableToken);
        }
      }
    } catch (err) {
      // Log but do not crash the request.
      console.error('Error in custom setHeaders:', err);
    }
  };

  // Return the standard static handler with our modified options.
  return express.static(root, options);
}

// ---- Application setup ----------------------------------------------------
const app = express();
const publicDir = path.join(__dirname, 'public');

// Ensure the public directory exists; create a dummy file if needed.
import fs from 'fs';
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir);
  fs.writeFileSync(path.join(publicDir, 'example.txt'), 'Hello, Express static!');
}

// Use the wrapper with immutable flag enabled and a maxAge of 1 year.
app.use('/static', staticWithImmutable(publicDir, { maxAge: 365 * 24 * 60 * 60 * 1000, immutable: true }));

// Fallback route.
app.get('/', (req: Request, res: Response) => {
  res.send('Visit /static/example.txt to see Cache‑Control header');
});

const server = app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');

  // Simple test request to verify header output.
  http.get('http://localhost:3000/static/example.txt', (resp) => {
    console.log('Received Cache-Control header:', resp.headers['cache-control']);
    resp.resume(); // drain response
    server.close();
  }).on('error', (e) => {
    console.error('Test request failed:', e);
    server.close();
  });
});