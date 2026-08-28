import http from 'http';
import url from 'url';
import { readFile } from 'fs/promises';
import { createHash } from 'crypto';

/**
 * Simple LRU Cache implementation using Map.
 * When isrMemoryCacheSize is 0 the cache is bypassed.
 */
class ISRCacheManager {
  private memoryCache: Map<string, any>;
  private maxSize: number;
  private edgeCache: Map<string, any>; // mock edge cache

  constructor(isrMemoryCacheSize: number) {
    this.maxSize = isrMemoryCacheSize;
    this.memoryCache = new Map();
    this.edgeCache = new Map(); // in real Next.js this would be unstable_cache
  }

  private makeKey(path: string): string {
    // simple hash to avoid long keys
    return createHash('md5').update(path).digest('hex');
  }

  get(path: string): any | undefined {
    const key = this.makeKey(path);
    // Try edge cache first
    if (this.edgeCache.has(key)) {
      return this.edgeCache.get(key);
    }
    // Memory cache only if size > 0
    if (this.maxSize > 0 && this.memoryCache.has(key)) {
      const value = this.memoryCache.get(key);
      // refresh LRU order
      this.memoryCache.delete(key);
      this.memoryCache.set(key, value);
      return value;
    }
    return undefined;
  }

  set(path: string, data: any): void {
    const key = this.makeKey(path);
    // Store in edge cache (mock)
    this.edgeCache.set(key, data);
    // Store in memory cache if enabled
    if (this.maxSize > 0) {
      if (this.memoryCache.size >= this.maxSize) {
        // evict oldest entry
        const oldestKey = this.memoryCache.keys().next().value;
        this.memoryCache.delete(oldestKey);
      }
      this.memoryCache.set(key, data);
    }
  }

  invalidate(path: string): void {
    const key = this.makeKey(path);
    this.edgeCache.delete(key);
    this.memoryCache.delete(key);
  }
}

// Configuration – change to 0 to reproduce the bug scenario
const isrMemoryCacheSize = 0; // set to 0 to bypass memory cache
const revalidateSeconds = 5;

const cacheManager = new ISRCacheManager(isrMemoryCacheSize);

/**
 * Simulated data source – reads JSON files from ./public.
 * If file does not exist or "enabled" flag is false, treat as 404.
 */
async function fetchData(path: string): Promise<any> {
  try {
    const filePath = `./public${path}.json`;
    const content = await readFile(filePath, { encoding: 'utf8' });
    const json = JSON.parse(content);
    if (json.enabled === 0) {
      // Simulate page being disabled/deleted
      throw new Error('Page disabled');
    }
    return json;
  } catch (err) {
    // Propagate as not found
    throw new Error('NotFound');
  }
}

/**
 * Handler for incoming HTTP requests.
 * Implements ISR logic: serve from cache, otherwise revalidate.
 */
async function requestHandler(req: http.IncomingMessage, res: http.ServerResponse) {
  const parsedUrl = url.parse(req.url || '/', true);
  const pathname = parsedUrl.pathname || '/';

  // Only handle /detail/:id routes for demo
  const match = pathname.match(/^\/detail\/(\d+)$/);
  if (!match) {
    res.statusCode = 404;
    res.end('Not Found');
    return;
  }
  const id = match[1];
  const cachePath = `/detail/${id}`;

  // Try cache first
  const cached = cacheManager.get(cachePath);
  if (cached) {
    res.setHeader('X-Cache', 'HIT');
    res.end(JSON.stringify(cached));
    return;
  }

  // Cache miss – fetch fresh data (revalidation)
  try {
    const data = await fetchData(cachePath);
    cacheManager.set(cachePath, data);
    // Set a timer to invalidate after revalidateSeconds
    setTimeout(() => cacheManager.invalidate(cachePath), revalidateSeconds * 1000);
    res.setHeader('X-Cache', 'MISS');
    res.end(JSON.stringify(data));
  } catch (e) {
    // If fetch fails, respond with 404
    res.statusCode = 404;
    res.end('Page not found');
  }
}

// Create HTTP server
const server = http.createServer((req, res) => {
  // Basic error handling wrapper
  requestHandler(req, res).catch(err => {
    console.error('Unexpected error:', err);
    res.statusCode = 500;
    res.end('Internal Server Error');
  });
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`ISR demo server listening on http://localhost:${PORT}`);
});