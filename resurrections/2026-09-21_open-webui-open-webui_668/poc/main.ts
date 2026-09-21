import { EventEmitter } from "events";

// Simulated AuthProvider interface from the application
export interface AuthProvider {
  initialize(): Promise<void>;
  authenticate(username: string, password: string): Promise<User | null>;
  syncUsers(): Promise<void>;
}

// Minimal User model used by Open‑WebUI
export interface User {
  id: string;
  username: string;
  email?: string;
  roles: string[];
}

// Configuration shape – normally validated with zod, but using plain checks
export interface LDAPConfig {
  host: string;
  bindDN: string;
  bindPassword: string;
  searchBase: string;
}

/**
 * LDAPAuthProvider – a proof‑of‑concept implementation.
 * It uses only Node's standard library; the real implementation would rely on
 * the `ldapjs` package (not present in the manifest) and a Fastify server.
 */
export class LDAPAuthProvider extends EventEmitter implements AuthProvider {
  private config: LDAPConfig;
  private connected: boolean = false;

  constructor(config: LDAPConfig) {
    super();
    this.validateConfig(config);
    this.config = config;
  }

  // Simple runtime validation – throws if required fields are missing
  private validateConfig(cfg: LDAPConfig) {
    const required = ["host", "bindDN", "bindPassword", "searchBase"];
    for (const key of required) {
      if (!cfg[key as keyof LDAPConfig]) {
        throw new Error(`LDAP config missing required field: ${key}`);
      }
    }
  }

  /**
   * Initialise the connection to the LDAP server.
   * In a real world scenario this would create an ldapjs client and bind.
   */
  async initialize(): Promise<void> {
    try {
      // Placeholder for LDAP bind – replace with actual client code.
      console.log(`Connecting to LDAP at ${this.config.host} as ${this.config.bindDN}`);
      // Simulate async bind operation
      await new Promise((res) => setTimeout(res, 100));
      this.connected = true;
      this.emit("ready");
    } catch (err) {
      console.error("Failed to initialise LDAP provider:", err);
      throw err;
    }
  }

  /**
   * Authenticate a user against LDAP.
   * Returns a User object on success or null on failure.
   */
  async authenticate(username: string, password: string): Promise<User | null> {
    if (!this.connected) {
      await this.initialize();
    }
    try {
      console.log(`Authenticating ${username} via LDAP`);
      // Simulated LDAP bind for the user – replace with real search + bind.
      await new Promise((res) => setTimeout(res, 100));
      // Mock successful authentication for any username that starts with "test"
      if (username.startsWith("test")) {
        const user: User = {
          id: `ldap-${username}`,
          username,
          email: `${username}@example.com`,
          roles: ["user"],
        };
        return user;
      }
      return null;
    } catch (err) {
      console.error("Authentication error:", err);
      return null;
    }
  }

  /**
   * Periodically sync LDAP users/groups into the local store.
   * Here we simply emit a "sync" event; the real implementation would query LDAP.
   */
  async syncUsers(): Promise<void> {
    if (!this.connected) {
      await this.initialize();
    }
    try {
      console.log("Starting LDAP user sync...");
      // Simulated delay for sync operation
      await new Promise((res) => setTimeout(res, 200));
      // Emit an event so the application can react (e.g., update DB)
      this.emit("sync", { timestamp: Date.now() });
      console.log("LDAP user sync completed.");
    } catch (err) {
      console.error("Error during LDAP sync:", err);
    }
  }
}

/**
 * Mock Fastify‑like plugin registration.
 * In the actual codebase this would be `fastify.register`.
 */
export function registerLDAPPlugin(app: any, config: LDAPConfig) {
  const provider = new LDAPAuthProvider(config);

  // Initialise provider once at startup
  provider.initialize().catch((e) => {
    console.error("Failed to start LDAP provider:", e);
    process.exit(1);
  });

  // Register a pre‑handler for the /login route
  app.addHook("preHandler", async (request: any, reply: any) => {
    if (request.raw.url !== "/login" || request.raw.method !== "POST") {
      return;
    }
    const { username, password } = request.body as { username: string; password: string };
    const user = await provider.authenticate(username, password);
    if (user) {
      // Attach user to request for downstream handlers
      request.user = user;
    } else {
      reply.code(401).send({ error: "Invalid credentials" });
    }
  });

  // Simulate a cron‑like background job using setInterval (Fastify cron plugin alternative)
  const syncIntervalMs = 5 * 60 * 1000; // every 5 minutes
  setInterval(() => {
    provider.syncUsers().catch((e) => console.error("Sync job failed:", e));
  }, syncIntervalMs);
}

// Example usage (would be in the server entry point)
if (require.main === module) {
  // Minimal mock of a Fastify instance with just the needed API
  const mockApp: any = {
    addHook: (hook: string, fn: Function) => {
      console.log(`Hook registered: ${hook}`);
      // In a real server, Fastify would call this for each request.
    },
  };

  const ldapConfig: LDAPConfig = {
    host: "ldap://localhost:389",
    bindDN: "cn=admin,dc=example,dc=com",
    bindPassword: "secret",
    searchBase: "ou=users,dc=example,dc=com",
  };

  registerLDAPPlugin(mockApp, ldapConfig);
  console.log("LDAP plugin registered – mock server running.");
}