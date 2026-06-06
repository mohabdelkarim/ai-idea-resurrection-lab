import { Router } from 'express';
import axios from 'axios';
import { Buffer } from 'buffer';

const router = Router();

// Assuming you have a settings model to store OpenRouter API credentials
import Settings from '../models/Settings';

router.post('/generate-image', async (req, res) => {
  try {
    const { prompt } = req.body;
    const settings = await Settings.findOne();
    if (!settings || !settings.openRouterApiKey) {
      return res.status(401).json({ error: 'OpenRouter API credentials are missing' });
    }

    const response = await axios.post('https://api.openrouter.ai/v1/generate', {
      prompt,
      model: 'google/gemini-2.5-flash-image-preview',
    }, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${settings.openRouterApiKey}`,
      },
    });

    if (response.status !== 200) {
      return res.status(response.status).json({ error: 'Failed to generate image' });
    }

    const imageBuffer = Buffer.from(response.data.image, 'base64');
    res.set('Content-Type', 'image/png');
    res.set('Content-Disposition', `attachment; filename=image.png`);
    res.send(imageBuffer);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Frontend code to send request to generate image
import { writable } from 'svelte/store';
import axios from 'axios';

const imageStore = writable(null);

async function generateImage(prompt) {
  try {
    const response = await axios.post('/generate-image', { prompt });
    const imageUrl = URL.createObjectURL(new Blob([response.data], { type: 'image/png' }));
    imageStore.set(imageUrl);
  } catch (error) {
    console.error(error);
  }
}

// Usage in Svelte component
<script>
  import { imageStore, generateImage } from './image-store.js';

  let prompt = '';

  async function handleSubmit() {
    await generateImage(prompt);
  }
</script>

<input bind:value={prompt} />
<button on:click={handleSubmit}>Generate Image</button>
<img src={$imageStore} alt='Generated Image' />