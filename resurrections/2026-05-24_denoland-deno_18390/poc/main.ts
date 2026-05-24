import { resolve } from 'path';
import { existsSync } from 'fs';
import { fileURLToPath } from 'url';

// Define a custom ImportMap resolver
class FallbackImportMapResolver {
  async resolve(specifier: string, _importMap: any) {
    // Check if the specifier ends with '.js'
    if (specifier.endsWith('.js')) {
      // Try to resolve the '.js' file
      const jsFilePath = resolve(specifier);
      if (existsSync(jsFilePath)) {
        return jsFilePath;
      }

      // If the '.js' file does not exist, try to resolve the '.ts' file
      const tsFilePath = specifier.replace('.js', '.ts');
      if (existsSync(tsFilePath)) {
        return tsFilePath;
      }
    }

    // If no fallback is needed, return the original specifier
    return specifier;
  }
}

// Create a new instance of the resolver
const resolver = new FallbackImportMapResolver();

// Define a test function
async function test() {
  try {
    // Test resolving a '.js' file that exists
    const jsFileSpecifier = './test.js';
    const jsFilePath = await resolver.resolve(jsFileSpecifier, {});
    console.log(`Resolved ${jsFileSpecifier} to ${jsFilePath}`);

    // Test resolving a '.js' file that does not exist, but a '.ts' file exists
    const tsFileSpecifier = './test.js';
    const tsFilePath = await resolver.resolve(tsFileSpecifier, {});
    console.log(`Resolved ${tsFileSpecifier} to ${tsFilePath}`);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
test();