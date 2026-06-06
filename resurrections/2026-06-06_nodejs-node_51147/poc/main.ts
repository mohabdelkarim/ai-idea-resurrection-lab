import * as fs from 'fs';
import * as path from 'path';

interface EnvFile {
  [key: string]: string;
}

function parseEnvFile(filePath: string): EnvFile {
  const envFile: EnvFile = {};
  try {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const lines = fileContent.split('\n');
    for (const line of lines) {
      const trimmedLine = line.trim();
      if (trimmedLine && !trimmedLine.startsWith('#')) {
        const [key, value] = trimmedLine.split('=');
        envFile[key.trim()] = value.trim();
      }
    }
  } catch (error) {
    console.error(`Error reading env file: ${error.message}`);
    process.exit(1);
  }
  return envFile;
}

function loadEnvFile(filePath: string) {
  const envFile = parseEnvFile(filePath);
  for (const [key, value] of Object.entries(envFile)) {
    process.env[key] = value;
  }
}

function main() {
  const nodeOptions = process.env.NODE_OPTIONS;
  if (nodeOptions) {
    const options = nodeOptions.split(' ');
    for (const option of options) {
      if (option.startsWith('--env-file=')) {
        const filePath = option.substring('--env-file='.length);
        loadEnvFile(filePath);
      }
    }
  }
}

main();
console.log(process.env);