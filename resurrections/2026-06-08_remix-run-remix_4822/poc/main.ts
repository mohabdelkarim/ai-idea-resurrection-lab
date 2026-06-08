import { RemixServer } from '@remix/run/server';
import express from 'express';
import { createRemixContext } from './context';

const app = express();

app.all('*', async (req, res, next) => {
  try {
    const remixContext = createRemixContext(req);
    const markup = await remixContext.render();
    // Add a check for DOM modifications before hydration
    const domModifications = checkDomModifications();
    if (domModifications) {
      // Handle DOM modifications, e.g., by re-rendering the page
      return res.status(500).send('Hydration failed due to DOM modifications');
    }
    res.send(markup);
  } catch (error) {
    next(error);
  }
});

function checkDomModifications() {
  // Simple implementation to check for DOM modifications
  const serverHtml = document.documentElement.outerHTML;
  const clientHtml = document.documentElement.outerHTML;
  return serverHtml !== clientHtml;
}

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send('Internal Server Error');
});

const port = 3000;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});