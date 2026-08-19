import http from 'http';
import path from 'path';
import { createServer, IncomingMessage, ServerResponse } from 'http';
import express, { Request, Response, NextFunction } from 'express';

// Core utilities module that re‑exports built‑ins
// ------------------------------------------------
// This module provides a single import surface for the framework.
// It lazily loads http.METHODS and converts them to lowercase.
// It also re‑exports Buffer and path.isAbsolute.

// utils.ts (simulated inline for PoC)
const CoreUtils = (() => {
  // Lazy load methods
  const getMethods = (): string[] => {
    // http.METHODS is an array of uppercase method names
    return http.METHODS.map((m) => m.toLowerCase());
  };

  // Exported members
  return {
    METHODS: getMethods(),
    isAbsolutePath: path.isAbsolute,
    BufferFrom: Buffer.from,
    BufferAlloc: Buffer.alloc,
    setProto: (obj: any, proto: any) => {
      // Guard for very old Node versions (pre‑v0.12) – not expected in modern envs
      if (typeof Object.setPrototypeOf === 'function') {
        Object.setPrototypeOf(obj, proto);
      } else {
        // Fallback – no‑op but kept for compatibility
      }
    },
  };
})();

// Simple middleware demonstrating removal of old deps
// ---------------------------------------------------
function bufferMiddleware(req: Request, res: Response, next: NextFunction) {
  try {
    // Use Buffer.from instead of safe-buffer
    const payload = CoreUtils.BufferFrom('Hello from bufferMiddleware');
    // Attach to request for downstream handlers
    (req as any).rawPayload = payload;
    next();
  } catch (err) {
    next(err);
  }
}

// Middleware that uses setPrototypeOf to mimic old behaviour
function prototypeMiddleware(req: Request, res: Response, next: NextFunction) {
  try {
    const parent = Object.getPrototypeOf(req);
    CoreUtils.setProto(req, parent);
    next();
  } catch (err) {
    next(err);
  }
}

// Route handler that checks absolute path using CoreUtils
function pathCheckHandler(req: Request, res: Response) {
  const testPath = req.query.path as string || '.';
  const isAbs = CoreUtils.isAbsolutePath(testPath);
  res.json({ path: testPath, isAbsolute: isAbs });
}

// Configuration merging using spread operator (replaces utils-merge)
interface ServerOptions {
  port?: number;
  host?: string;
  greeting?: string;
}
const defaultOptions: ServerOptions = { port: 3000, host: '127.0.0.1', greeting: 'Hello' };
function mergeOptions(opts: ServerOptions): ServerOptions {
  // Typescript overloads preserve type safety automatically
  return { ...defaultOptions, ...opts };
}

// Application setup
const app = express();
app.use(express.json());
app.use(bufferMiddleware);
app.use(prototypeMiddleware);

app.get('/methods', (req: Request, res: Response) => {
  // Expose the computed methods list
  res.json({ methods: CoreUtils.METHODS });
});

app.get('/path-check', pathCheckHandler);

app.post('/echo', (req: Request, res: Response) => {
  // Echo back the raw payload created earlier
  const payload: Buffer = (req as any).rawPayload;
  res.type('text/plain').send(payload);
});

// Error handling middleware
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  console.error('Error:', err);
  res.status(500).json({ error: err?.message || 'Internal Server Error' });
});

// Start server with merged options
const userOptions: ServerOptions = { port: 4000, greeting: 'Hi there' };
const finalOptions = mergeOptions(userOptions);

const server = createServer(app);
server.listen(finalOptions.port, finalOptions.host, () => {
  console.log(`${finalOptions.greeting}! Server listening on http://${finalOptions.host}:${finalOptions.port}`);
});