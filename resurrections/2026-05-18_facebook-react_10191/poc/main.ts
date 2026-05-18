import * as fs from 'fs';
import * as path from 'path';
import * as chalk from 'chalk';

const LICENSE_HEADER = `// Copyright 2023 Facebook, Inc.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

`;

function updateLicenseHeader(filePath: string): void {
  try {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    if (!fileContent.startsWith(LICENSE_HEADER)) {
      console.log(chalk.green(`Updating license header for ${filePath}...`));
      const newContent = LICENSE_HEADER + fileContent;
      fs.writeFileSync(filePath, newContent);
    }
  } catch (error) {
    console.error(chalk.red(`Error updating ${filePath}: ${error.message}`));
  }
}

function main(): void {
  const rootDir = './packages';
  const filesToUpdate = [];

  function walkDir(dir: string) {
    const files = fs.readdirSync(dir);
    files.forEach((file) => {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      if (stat.isDirectory()) {
        walkDir(filePath);
      } else if (file.endsWith('.ts') || file.endsWith('.tsx')) {
        filesToUpdate.push(filePath);
      }
    });
  }

  walkDir(rootDir);

  filesToUpdate.forEach((filePath) => {
    updateLicenseHeader(filePath);
  });
}

main();