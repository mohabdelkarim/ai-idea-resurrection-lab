import * as ts from 'typescript';

// Define a function to get the completion suggestions
function getCompletionSuggestions(filePath: string, position: number): string[] {
  try {
    // Create a TypeScript program
    const program = ts.createProgram([filePath], {
      allowJs: true,
      // Use the default compiler options
      compilerOptions: ts.getDefaultCompilerOptions(),
    });

    // Get the source file
    const sourceFile = program.getSourceFile(filePath);
    if (!sourceFile) {
      throw new Error(`Could not find source file: ${filePath}`);
    }

    // Get the completion context
    const completionContext = ts.getCompletionContextAtPosition(sourceFile, position);
    if (!completionContext) {
      return [];
    }

    // Get the completion suggestions
    const suggestions = ts.getCompletionEntriesAtPosition(completionContext);
    return suggestions.map((suggestion) => suggestion.name);
  } catch (error) {
    console.error(`Error getting completion suggestions: ${error}`);
    return [];
  }
}

// Example usage
interface Options {
  borderColor: 'black' | 'red' | 'green' | 'yellow' | 'blue' | string;
}

const opts: Options = { borderColor: 'red' };

// Get the completion suggestions
const filePath = './example.ts';
const position = 37; // Position of the cursor in the example file
const suggestions = getCompletionSuggestions(filePath, position);
console.log(suggestions);