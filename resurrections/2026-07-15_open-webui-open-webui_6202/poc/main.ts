import { Collection, URL } from './models.ts';

class URLCollection {
  private collections: Collection[];

  constructor() {
    this.collections = [];
  }

  public addCollection(name: string): Collection {
    const collection = new Collection(name);
    this.collections.push(collection);
    return collection;
  }

  public addURLToCollection(collectionName: string, url: string, auth?: { type: 'basic' | 'token', credentials: string }): URL {
    const collection = this.collections.find(c => c.name === collectionName);
    if (!collection) {
      throw new Error(`Collection ${collectionName} not found`);
    }
    const urlObject = new URL(url, auth);
    collection.urls.push(urlObject);
    return urlObject;
  }

  public async scanCollection(collectionName: string): Promise<void> {
    const collection = this.collections.find(c => c.name === collectionName);
    if (!collection) {
      throw new Error(`Collection ${collectionName} not found`);
    }
    for (const url of collection.urls) {
      try {
        await url.scan();
      } catch (error) {
        console.error(`Error scanning ${url.url}: ${error}`);
      }
    }
  }

  public scheduleScan(collectionName: string, interval: number): void {
    const collection = this.collections.find(c => c.name === collectionName);
    if (!collection) {
      throw new Error(`Collection ${collectionName} not found`);
    }
    setInterval(async () => {
      await this.scanCollection(collectionName);
    }, interval);
  }
}

class Collection {
  public name: string;
  public urls: URL[];

  constructor(name: string) {
    this.name = name;
    this.urls = [];
  }
}

class URL {
  public url: string;
  public auth?: { type: 'basic' | 'token', credentials: string };
  private content: string;

  constructor(url: string, auth?: { type: 'basic' | 'token', credentials: string }) {
    this.url = url;
    this.auth = auth;
    this.content = '';
  }

  public async scan(): Promise<void> {
    try {
      const response = await fetch(this.url, {
        headers: {
          Authorization: this.auth?.type === 'basic' ? `Basic ${this.auth.credentials}` : `Bearer ${this.auth?.credentials}`
        }
      });
      const html = await response.text();
      this.content = html;
    } catch (error) {
      console.error(`Error fetching ${this.url}: ${error}`);
    }
  }
}

const urlCollection = new URLCollection();
const collection = urlCollection.addCollection('My Collection');
urlCollection.addURLToCollection('My Collection', 'https://example.com', { type: 'basic', credentials: 'user:pass' });
urlCollection.scheduleScan('My Collection', 60000);