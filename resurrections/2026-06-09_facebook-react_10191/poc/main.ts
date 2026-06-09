import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

async function updateLicense(filePath: string, newLicense: string) {
  try {
    const fileContent = await readFile(filePath, 'utf8');
    const updatedContent = fileContent.replace(/old license/g, newLicense);
    await writeFile(filePath, updatedContent);
    console.log(`Updated license in ${filePath}`);
  } catch (error) {
    console.error(`Error updating license in ${filePath}: ${error.message}`);
  }
}

async function main() {
  const filesToUpdate = ['path/to/file1.js', 'path/to/file2.js'];
  const newLicense = 'Apache License v2.0';

  for (const file of filesToUpdate) {
    await updateLicense(file, newLicense);
  }
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});

// Additional code to demonstrate compatibility with existing dependencies
import { rollup } from 'rollup';
import { babel } from '@rollup/plugin-babel';

async function build() {
  try {
    const bundle = await rollup({
      input: 'src/index.js',
      plugins: [babel({
        babelHelpers: 'bundled',
      })],
    });
    await bundle.write({
      file: 'dist/bundle.js',
      format: 'cjs',
    });
    console.log('Built bundle');
  } catch (error) {
    console.error('Error building bundle:', error);
  }
}

build();