import express, { Request, Response, NextFunction } from 'express';
import JSON5 from 'json-bigint';

const app = express();

// Define a type for the stringifier option
type Stringifier = (data: any) => string;

// Define a default stringifier that falls back to JSON.stringify
const defaultStringifier: Stringifier = (data) => JSON.stringify(data);

// Define a custom stringifier option for res.json()
interface ResJsonOptions {
  stringifier?: Stringifier;
}

// Update the res.json() method to accept the new option
app.use((req: Request, res: Response, next: NextFunction) => {
  res.json = (data: any, options?: ResJsonOptions) => {
    if (options && options.stringifier) {
      res.send(options.stringifier(data));
    } else {
      res.send(defaultStringifier(data));
    }
  };
  next();
});

// Test the res.json() method with the custom stringifier
app.get('/test', (req: Request, res: Response) => {
  try {
    const data = { foo: 'bar' };
    res.json(data, { stringifier: JSON5.stringify });
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal Server Error');
  }
});

// Start the server
const port = 3000;
app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err);
  res.status(500).send('Internal Server Error');
});