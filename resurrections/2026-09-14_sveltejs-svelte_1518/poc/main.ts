import * as fs from 'fs';
import * as path from 'path';

/** Simple representation of a source location */
interface SourceLocation {
  line: number;
  column: number;
  start: number; // index in source string
  end: number;   // index in source string
}

/** Diagnostic emitted by the compiler */
interface Diagnostic {
  message: string;
  location: SourceLocation;
  snippet: string; // original template snippet
}

/** Configuration flag for enhanced errors */
const config = {
  enhancedErrors: true,
};

/** Utility to read a file and return its content */
function readTemplate(filePath: string): string {
  try {
    return fs.readFileSync(filePath, 'utf-8');
  } catch (e) {
    throw new Error(`Unable to read template: ${e instanceof Error ? e.message : e}`);
  }
}

/** Very naive parser that finds {#each ...} blocks and records their location */
function parseEachBlocks(source: string): SourceLocation[] {
  const locations: SourceLocation[] = [];
  const eachRegex = /{#each\s+([^}]+)\s+as\s+([^}]+)}/g;
  let match: RegExpExecArray | null;
  while ((match = eachRegex.exec(source)) !== null) {
    const start = match.index;
    const end = eachRegex.lastIndex;
    const before = source.slice(0, start);
    const line = before.split('\n').length;
    const column = start - before.lastIndexOf('\n') - 1;
    locations.push({ line, column, start, end });
  }
  return locations;
}

/** Simulated runtime that checks if a variable is defined */
function runtimeCheck(varName: string, context: Record<string, any>): void {
  if (!(varName in context) || context[varName] === undefined) {
    throw new Error(`${varName} is undefined`);
  }
}

/** Compile function that produces diagnostics on failure */
function compileTemplate(filePath: string, context: Record<string, any>): void {
  const source = readTemplate(filePath);
  const eachBlocks = parseEachBlocks(source);
  for (const loc of eachBlocks) {
    const blockText = source.slice(loc.start, loc.end);
    const varMatch = /{#each\s+([^\s]+)\s+as/.exec(blockText);
    const varName = varMatch ? varMatch[1] : 'unknown';
    try {
      runtimeCheck(varName, context);
    } catch (e) {
      if (config.enhancedErrors) {
        const diagnostic: Diagnostic = {
          message: `${varName} is undefined in ${blockText}`,
          location: loc,
          snippet: getSnippet(source, loc),
        };
        const formatted = formatDiagnostic(diagnostic);
        console.error(formatted);
        // In real compiler we would attach source maps here
      } else {
        throw e;
      }
    }
  }
}

/** Extract a few lines around the error location for context */
function getSnippet(source: string, loc: SourceLocation, contextLines = 2): string {
  const lines = source.split('\n');
  const startLine = Math.max(loc.line - contextLines - 1, 0);
  const endLine = Math.min(loc.line + contextLines, lines.length);
  return lines.slice(startLine, endLine).join('\n');
}

/** Format a diagnostic into a human‑readable string */
function formatDiagnostic(diag: Diagnostic): string {
  const { line, column } = diag.location;
  return `Error: ${diag.message}\n` +
    `At line ${line}, column ${column}:\n` +
    `--- Template context ---\n` +
    `${diag.snippet}\n` +
    `------------------------`;
}

/** Example usage */
function main() {
  const templatePath = path.resolve('example.svelte');
  // Write a tiny template for demonstration
  const exampleTemplate = `<script>let items;</script>\n{#each items as item}\n  <p>{item}</p>\n{/each}`;
  fs.writeFileSync(templatePath, exampleTemplate, 'utf-8');

  // Empty context to trigger the error
  const context = {};
  compileTemplate(templatePath, context);

  // Clean up
  fs.unlinkSync(templatePath);
}

// Run only when this file is executed directly
if (require.main === module) {
  try {
    main();
  } catch (e) {
    console.error('Unhandled exception:', e);
    process.exit(1);
  }
}