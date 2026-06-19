import * as ts from "typescript";

interface UMDModuleOptions {
  moduleName: string;
  globalNamespace: string;
}

function generateUMDModule(factory: string, options: UMDModuleOptions): string {
  const { moduleName, globalNamespace } = options;
  return `(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
      define(factory);
    } else if (typeof exports === 'object') {
      module.exports = factory(require, exports, module);
    } else {
      root.${globalNamespace} = factory();
    }
  }(this, function(require, exports, module) {
    ${factory}
  }));`;
}

function compileTypeScript(filePath: string, content: string, options: UMDModuleOptions): string {
  try {
    const sourceFile = ts.createSourceFile(filePath, content, ts.ScriptTarget.ES2015);
    const factory = ts.getEmitHost().getSourceFileFactory();
    const printer = ts.createPrinter();
    const statements = sourceFile.statements;
    const umdModule = generateUMDModule(printer.printList(statements), options);
    return umdModule;
  } catch (error) {
    console.error(error);
    throw error;
  }
}

// Example usage:
const filePath = "example.ts";
const content = "export function add(a: number, b: number) { return a + b; }";
const options: UMDModuleOptions = {
  moduleName: "example",
  globalNamespace: "exampleNamespace"
};

const compiledCode = compileTypeScript(filePath, content, options);
console.log(compiledCode);