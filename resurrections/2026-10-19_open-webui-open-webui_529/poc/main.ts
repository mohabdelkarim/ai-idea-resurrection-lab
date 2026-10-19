import * as http from 'http';
import * as url from 'url';
import { readFileSync } from 'fs';

// ---------- Types ----------
interface RagConfig {
  vectorStore: 'pinecone' | 'qdrant' | 'faiss';
  documents: string[]; // URIs
}

interface ModelFile {
  id: string;
  name: string;
  description?: string;
  ragConfig?: RagConfig;
}

// ---------- Simple In‑Memory Store ----------
const modelStore: Record<string, ModelFile> = {};

// ---------- Vector Store Interfaces ----------
interface VectorStore {
  upsert(docs: string[]): Promise<void>;
}

class PineconeStore implements VectorStore {
  async upsert(docs: string[]): Promise<void> {
    console.log('Pinecone upsert:', docs);
    // placeholder for real API call
  }
}

class QdrantStore implements VectorStore {
  async upsert(docs: string[]): Promise<void> {
    console.log('Qdrant upsert:', docs);
  }
}

class FaissStore implements VectorStore {
  async upsert(docs: string[]): Promise<void> {
    console.log('FAISS upsert:', docs);
  }
}

// ---------- RagService ----------
class RagService {
  private storeFactory: (type: RagConfig['vectorStore']) => VectorStore;

  constructor() {
    // Dependency injection via simple factory
    this.storeFactory = (type) => {
      switch (type) {
        case 'pinecone': return new PineconeStore();
        case 'qdrant': return new QdrantStore();
        case 'faiss': return new FaissStore();
        default: throw new Error(`Unsupported vector store: ${type}`);
      }
    };
  }

  async processRagConfig(rag: RagConfig): Promise<void> {
    try {
      // Simulate loading documents (in real code use LangChain loaders)
      const loadedDocs = rag.documents.map((uri) => `content-of-${uri}`);
      const store = this.storeFactory(rag.vectorStore);
      await store.upsert(loadedDocs);
    } catch (err) {
      console.error('RagService error:', err);
      throw err;
    }
  }
}

const ragService = new RagService();

// ---------- Simple JSON Schema Validation ----------
function validateModelFile(payload: any): ModelFile {
  if (typeof payload.id !== 'string' || typeof payload.name !== 'string') {
    throw new Error('Invalid ModelFile: id and name are required strings');
  }
  if (payload.ragConfig) {
    const rc = payload.ragConfig;
    if (!['pinecone','qdrant','faiss'].includes(rc.vectorStore)) {
      throw new Error('Invalid vectorStore in ragConfig');
    }
    if (!Array.isArray(rc.documents)) {
      throw new Error('ragConfig.documents must be an array');
    }
  }
  return payload as ModelFile;
}

// ---------- HTTP Controller ----------
function handleRequest(req: http.IncomingMessage, res: http.ServerResponse) {
  const parsedUrl = url.parse(req.url || '', true);
  if (req.method === 'POST' && parsedUrl.pathname === '/model') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', async () => {
      try {
        const payload = JSON.parse(body);
        const model = validateModelFile(payload);
        modelStore[model.id] = model;
        if (model.ragConfig) {
          await ragService.processRagConfig(model.ragConfig);
        }
        res.writeHead(201, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'created', id: model.id }));
      } catch (e:any) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  if (req.method === 'PUT' && parsedUrl.pathname?.startsWith('/model/')) {
    const id = parsedUrl.pathname.split('/')[2];
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', async () => {
      try {
        if (!modelStore[id]) throw new Error('Model not found');
        const payload = JSON.parse(body);
        const model = validateModelFile({ ...modelStore[id], ...payload });
        modelStore[id] = model;
        if (model.ragConfig) {
          await ragService.processRagConfig(model.ragConfig);
        }
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'updated', id }));
      } catch (e:any) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // Fallback
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
}

// ---------- Server Startup ----------
const server = http.createServer(handleRequest);
server.listen(3000, () => {
  console.log('ModelFile API listening on http://localhost:3000');
});