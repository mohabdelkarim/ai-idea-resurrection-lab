import * as fs from 'fs';
import * as path from 'path';
import { parse, compile } from 'svelte/compiler';

// Define a custom range block syntax
function rangeBlock(node: any, compiler: any) {
  if (node.type === 'range') {
    const { start, end, variable } = node;
    const rangeExpression = `${start}...${end}`;
    const eachBlock = {
      type: 'each',
      expression: rangeExpression,
      variable: variable,
      content: node.content,
    };
    return compiler(eachBlock);
  }
}

// Define a custom Svelte compiler with range block support
function customCompiler(source: string) {
  try {
    const ast = parse(source);
    const modifiedAst = ast.body.map((node: any) => {
      if (node.type === 'range') {
        return rangeBlock(node, compile);
      }
      return node;
    });
    const compiled = compile({
      type: 'component',
      name: 'RangeBlock',
      imports: [],
      body: modifiedAst,
    });
    return compiled.code;
  } catch (error: any) {
    console.error('Error compiling Svelte code:', error);
    throw error;
  }
}

// Test the custom compiler
const svelteCode = `
  {#range 1..5 as n}
    {n}
  {/range}
`;
const compiledCode = customCompiler(svelteCode);
console.log(compiledCode);

// Write the compiled code to a file
fs.writeFileSync(path.join(__dirname, 'compiled.js'), compiledCode);

// Use the compiled code
import { createApp } from 'svelte';
const app = createApp({ compiledCode });
app.mount('#app');