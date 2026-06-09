import * as http2 from 'http2';
import * as fs from 'fs';
import * as path from 'path';
import express, { Request, Response, NextFunction } from 'express';

const app = express();

app.use((req: Request, res: Response, next: NextFunction) => {
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

app.get('/', (req: Request, res: Response) => {
  res.send('Hello World!');
});

const privateKey = fs.readFileSync(path.join(__dirname, 'private.key'), 'utf8');
const certificate = fs.readFileSync(path.join(__dirname, 'certificate.crt'), 'utf8');

const credentials = {
  key: privateKey,
  cert: certificate
};

http2.createSecureServer(credentials).on('stream', (stream, headers) => {
  app.handle(req, res);
  stream.respond({
    'content-type': 'text/html; charset=utf-8',
    ':status': 200
  });
  stream.end('Hello World!');
}).listen(3000, () => {
  console.log('Server listening on port 3000');
});