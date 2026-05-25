import express, { Request, Response } from 'express';
import cookie from 'cookie';

const app = express();
app.use(express.json());

interface CookieOptions {
  httpOnly?: boolean;
  secure?: boolean;
  sameSite?: string;
  maxAge?: number;
  expires?: Date;
  domain?: string;
  path?: string;
  partitioned?: boolean;
}

app.get('/set-cookie', (req: Request, res: Response) => {
  const options: CookieOptions = {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 3600000,
    partitioned: true,
  };
  res.cookie('test', 'value', options);
  res.send('Cookie set');
});

app.get('/get-cookie', (req: Request, res: Response) => {
  const cookies = cookie.parse(req.headers.cookie);
  res.json(cookies);
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});

try {
  app.emit('error', new Error('Test error'));
} catch (error) {
  console.error(error);
}