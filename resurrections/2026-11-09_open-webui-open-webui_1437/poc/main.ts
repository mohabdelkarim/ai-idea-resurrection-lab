import fetch from 'node-fetch'; // node-fetch is not in manifest, fallback to built‑in https
import { URL } from 'url';

/**
 * Generic provider interface for AI services.
 */
export interface Provider {
  /**
   * Send a chat message and receive a streamed response.
   */
  chat(messages: ChatMessage[]): AsyncIterable<string>;

  /**
   * Get a completion for a prompt.
   */
  completion(prompt: string): Promise<string>;

  /**
   * Generate speech from text.
   */
  tts(text: string): Promise<Buffer>;

  /**
   * Transcribe speech to text.
   */
  stt(audio: Buffer): Promise<string>;

  /**
   * Generate an image from a prompt.
   */
  image(prompt: string): Promise<Buffer>;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

/**
 * Simple error mapping for LocalAI responses.
 */
class LocalAIError extends Error {
  constructor(public code: string, message: string) {
    super(message);
    this.name = 'LocalAIError';
  }
}

/**
 * Provider implementation that talks to a LocalAI server exposing OpenAI‑compatible endpoints.
 */
export class LocalAIProvider implements Provider {
  private baseUrl: string;
  private apiKey: string;

  constructor(config: { endpoint: string; apiKey: string }) {
    this.baseUrl = config.endpoint.replace(/\/+$/, ''); // strip trailing slash
    this.apiKey = config.apiKey;
  }

  private async request(path: string, body: any, stream: boolean = false): Promise<any> {
    const url = new URL(path, this.baseUrl).toString();
    const headers: any = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.apiKey}`,
    };
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new LocalAIError(err.error?.code || response.status.toString(), err.error?.message || response.statusText);
    }
    return stream ? response.body : response.json();
  }

  async *chat(messages: ChatMessage[]): AsyncIterable<string> {
    const body = { model: 'localai', messages, stream: true };
    const stream = await this.request('/v1/chat/completions', body, true);
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        // Assume each line is a JSON object with a "content" field.
        for (const line of chunk.split('\n')) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            if (data.choices && data.choices[0]?.delta?.content) {
              yield data.choices[0].delta.content;
            }
          } catch (e) {
            // ignore malformed lines
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async completion(prompt: string): Promise<string> {
    const body = { model: 'localai', prompt, max_tokens: 256 };
    const result = await this.request('/v1/completions', body);
    return result.choices?.[0]?.text ?? '';
  }

  async tts(text: string): Promise<Buffer> {
    const body = { model: 'localai-tts', input: text };
    const resp = await this.request('/v1/audio/speech', body);
    // Assuming the API returns base64 audio
    const base64 = resp.audio_content;
    return Buffer.from(base64, 'base64');
  }

  async stt(audio: Buffer): Promise<string> {
    const body = { model: 'localai-stt', audio: audio.toString('base64') };
    const result = await this.request('/v1/audio/transcriptions', body);
    return result.text ?? '';
  }

  async image(prompt: string): Promise<Buffer> {
    const body = { prompt, n: 1, size: '256x256' };
    const result = await this.request('/v1/images/generations', body);
    const url = result.data?.[0]?.url;
    if (!url) throw new Error('Image generation failed');
    const imgResp = await fetch(url);
    if (!imgResp.ok) throw new Error('Failed to download generated image');
    const arrayBuf = await imgResp.arrayBuffer();
    return Buffer.from(arrayBuf);
  }
}

/**
 * Example usage demonstrating provider selection.
 */
async function demo() {
  const config = { endpoint: 'http://localhost:8080', apiKey: 'sk-localai' };
  const provider: Provider = new LocalAIProvider(config);
  console.log('--- Completion Demo ---');
  const comp = await provider.completion('Hello world');
  console.log('Completion:', comp);

  console.log('--- Chat Stream Demo ---');
  const messages: ChatMessage[] = [{ role: 'user', content: 'Tell me a joke' }];
  for await (const chunk of provider.chat(messages)) {
    process.stdout.write(chunk);
  }
  console.log('\n');
}

// Run demo if this file is executed directly
if (require.main === module) {
  demo().catch((err) => {
    if (err instanceof LocalAIError) {
      console.error(`LocalAI error [${err.code}]: ${err.message}`);
    } else {
      console.error('Unexpected error:', err);
    }
    process.exit(1);
  });
}