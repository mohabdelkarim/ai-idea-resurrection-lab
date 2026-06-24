import { fileURLToPath } from 'url';
import { createServer, type Server } from 'http';
import { createViteServer } from 'vite';
import type { ViteServer } from 'vite';

async function startViteServer(): Promise<ViteServer> {
  const viteServer = await createViteServer({
    server: {
      middlewareMode: true,
    },
    build: {
      watch: true,
    },
  });
  await viteServer.listen(5173);
  return viteServer;
}

async function startCustomServer(): Promise<Server> {
  return new Promise((resolve) => {
    const server = createServer((req, res) => {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end('Hello from custom server!');
    });
    server.listen(8080, () => {
      resolve(server);
    });
  });
}

async function main() {
  try {
    const viteServer = await startViteServer();
    const customServer = await startCustomServer();
    console.log('Vite server listening on port 5173');
    console.log('Custom server listening on port 8080');
  } catch (error) {
    console.error(error);
    process.exit(1);
  }
}

main();