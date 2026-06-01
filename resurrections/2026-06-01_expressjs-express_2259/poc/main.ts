import * as http from 'http';
import * as url from 'url';
import { promisify } from 'util';

interface Request {
  url: string;
  method: string;
  headers: any;
  body: any;
}

interface Response {
  statusCode: number;
  headers: any;
  send: (data: any) => void;
}

interface NextFunction {
  (): Promise<void>;
  (err: Error): Promise<void>;
}

type MiddlewareFunction = (req: Request, res: Response, next: NextFunction) => Promise<void> | void;

class Express {
  private middleware: MiddlewareFunction[] = [];

  use(middleware: MiddlewareFunction) {
    this.middleware.push(middleware);
  }

  async handleRequest(req: Request, res: Response) {
    try {
      await this.runMiddleware(req, res, 0);
      res.statusCode = 404;
      res.send('Not Found');
    } catch (err) {
      this.handleError(err, req, res);
    }
  }

  private async runMiddleware(req: Request, res: Response, index: number) {
    if (index >= this.middleware.length) return;

    const middleware = this.middleware[index];
    const next = async (err?: Error) => {
      if (err) {
        throw err;
      }
      await this.runMiddleware(req, res, index + 1);
    };

    const result = middleware(req, res, next);
    if (result instanceof Promise) {
      await result;
    }
  }

  private handleError(err: Error, req: Request, res: Response) {
    console.error(err);
    res.statusCode = 500;
    res.send('Internal Server Error');
  }
}

const express = new Express();

// Example middleware
const exampleMiddleware: MiddlewareFunction = async (req, res, next) => {
  try {
    // Simulate async operation
    await new Promise((resolve) => setTimeout(resolve, 100));
    req.body = { message: 'Hello, World!' };
    await next();
  } catch (err) {
    await next(err);
  }
};

express.use(exampleMiddleware);

// Example error handler
const errorHandler: MiddlewareFunction = async (req, res, next) => {
  try {
    await next();
  } catch (err) {
    console.error(err);
    res.statusCode = 500;
    res.send('Internal Server Error');
  }
};

express.use(errorHandler);

// Create HTTP server
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const request: Request = {
    url: parsedUrl.pathname,
    method: req.method,
    headers: req.headers,
    body: null,
  };
  const response: Response = {
    statusCode: 200,
    headers: {},
    send: (data) => {
      res.writeHead(response.statusCode, response.headers);
      res.end(data);
    },
  };
  express.handleRequest(request, response);
});

// Start server
server.listen(3000, () => {
  console.log('Server started on port 3000');
});