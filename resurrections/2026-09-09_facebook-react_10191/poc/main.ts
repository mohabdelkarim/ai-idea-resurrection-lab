import * as fs from 'fs';
import * as path from 'path';

/**
 * Simple CI helper that verifies the presence and basic validity of a dual
 * license file (LICENSE.dual) and ensures the package.json license field uses
 * the correct SPDX expression.
 *
 * This is a proof‑of‑concept and does not perform full SPDX parsing – it only
 * checks that the expected strings are present.
 */

const PROJECT_ROOT = process.cwd();
const LICENSE_FILE = path.join(PROJECT_ROOT, 'LICENSE.dual');
const PACKAGE_JSON = path.join(PROJECT_ROOT, 'package.json');
const EXPECTED_SPDX = 'Apache-2.0 OR GPL-2.0-only';

function readFileSafe(filePath: string): string | null {
  try {
    return fs.readFileSync(filePath, {encoding: 'utf8'});
  } catch (err) {
    console.error(`Error reading ${filePath}:`, (err as Error).message);
    return null;
  }
}

function verifyLicenseFile(content: string): boolean {
  const hasApache = /Apache\s*License\s*v?2\.0/i.test(content);
  const hasGPL = /GNU\s+General\s+Public\s+License\s+Version\s+2/i.test(content);
  if (!hasApache) {
    console.error('LICENSE.dual is missing Apache‑2.0 text.');
  }
  if (!hasGPL) {
    console.error('LICENSE.dual is missing GPL‑2.0 text.');
  }
  return hasApache && hasGPL;
}

function verifyPackageJson(content: string): boolean {
  try {
    const pkg = JSON.parse(content);
    if (!pkg.license) {
      console.error('package.json missing \"license\" field.');
      return false;
    }
    if (pkg.license !== EXPECTED_SPDX) {
      console.error(`package.json license field is \"${pkg.license}\", expected \"${EXPECTED_SPDX}\".`);
      return false;
    }
    return true;
  } catch (err) {
    console.error('Failed to parse package.json:', (err as Error).message);
    return false;
  }
}

function main(): void {
  const licenseContent = readFileSafe(LICENSE_FILE);
  if (!licenseContent) {
    process.exit(1);
  }
  const pkgContent = readFileSafe(PACKAGE_JSON);
  if (!pkgContent) {
    process.exit(1);
  }

  const licenseOk = verifyLicenseFile(licenseContent);
  const pkgOk = verifyPackageJson(pkgContent);

  if (licenseOk && pkgOk) {
    console.log('✅ Dual license verification passed.');
    process.exit(0);
  } else {
    console.error('❌ Dual license verification failed.');
    process.exit(1);
  }
}

// Execute when run directly
if (require.main === module) {
  main();
}