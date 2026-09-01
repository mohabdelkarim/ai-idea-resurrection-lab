import * as http from 'http';
import * as url from 'url';

/**
 * Simple representation of Astro's Vite preview config.
 */
interface VitePreviewConfig {
  allowedHosts?: boolean | string[]; // true means any host, array means whitelist
  host?: string; // hostname to bind, e.g., '0.0.0.0'
  port?: number; // port number
}

/**
 * PreviewConfig bridges Astro config to Vite preview options.
 */
class PreviewConfig {
  allowedHosts: Set<string>;
  host: string;
  port: number;

  constructor(viteConfig: VitePreviewConfig) {
    // Default values
    this.host = viteConfig.host ?? 'localhost';
    this.port = viteConfig.port ?? 3000;

    // Resolve allowed hosts
    if (viteConfig.allowedHosts === true) {
      // any host allowed – represent by empty set meaning unrestricted
      this.allowedHosts = new Set();
    } else if (Array.isArray(viteConfig.allowedHosts)) {
      this.allowedHosts = new Set(viteConfig.allowedHosts);
    } else {
      // false or undefined -> only localhost allowed
      this.allowedHosts = new Set(['localhost', '127.0.0.1']);
    }
  }

  /**
   * Checks whether the incoming request host is permitted.
   */
  isHostAllowed(requestHost: string): boolean {
    // Empty set means any host is allowed
    if (this.allowedHosts.size === 0) return true;
    // Strip port if present
    const hostOnly = requestHost.split(':')[0];
    return this.allowedHosts.has(hostOnly);
  }
}

/**
 * Mock function that would be called by Astro's CLI preview command.
 */
function startPreview(viteConfig: VitePreviewConfig) {
  try {
    const preview = new PreviewConfig(viteConfig);
    const server = http.createServer((req, res) => {
      const parsedUrl = url.parse(req.url || '/');
      const hostHeader = req.headers.host;
      if (!hostHeader) {
        res.statusCode = 400;
        res.end('Bad Request: Missing Host header');
        return;
      }

      if (!preview.isHostAllowed(hostHeader)) {
        res.statusCode = 403;
        res.end(`Blocked request. This host ("${hostHeader}") is not allowed.`);
        return;
      }

      // Simple response for allowed hosts
      res.statusCode = 200;
      res.setHeader('Content-Type', 'text/plain');
      res.end(`Hello from preview server! You accessed ${parsedUrl.pathname}`);
    });

    server.listen(preview.port, preview.host, () => {
      console.log(`Preview server listening on http://${preview.host}:${preview.port}`);
      console.log(`Allowed hosts: ${preview.allowedHosts.size === 0 ? 'any' : Array.from(preview.allowedHosts).join(', ')}`);
    });
  } catch (err) {
    console.error('Failed to start preview:', err);
    process.exit(1);
  }
}

// Example usage – this would normally come from astro.config.ts
const astroConfig = {
  vite: {
    preview: {
      allowedHosts: ['my-hostname', 'example.local'], // try true, false, or []
      host: '0.0.0.0',
      port: 54321,
    },
  },
};

// Invoke the preview with the extracted config
startPreview(astroConfig.vite.preview);