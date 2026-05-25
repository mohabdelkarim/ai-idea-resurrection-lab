import { TSESTree } from '@typescript-eslint/experimental-utils';
import * as fs from 'fs';
import * as path from 'path';
import { LintResult, SuppressedError } from 'eslint';

// Define a new class to handle suppression reminders
class SuppressionsReminder {
  private lintResults: LintResult[];

  constructor(lintResults: LintResult[]) {
    this.lintResults = lintResults;
  }

  // Process lint results and emit informational diagnostics for suppressed errors
  processResults(): void {
    this.lintResults.forEach((result) => {
      const suppressedErrors: SuppressedError[] = result.suppressedErrors || [];
      if (suppressedErrors.length > 0) {
        const message = `${suppressedErrors.length} errors were suppressed in this file`;
        // Emit an informational diagnostic
        result.messages.push({
          message,
          severity: 0, // Info level
          from: 'suppressions-reminder',
        });
      }
    });
  }
}

// Define a function to integrate with ESLint's CLI
function remindSuppressions(lintResults: LintResult[]): void {
  try {
    const reminder = new SuppressionsReminder(lintResults);
    reminder.processResults();
  } catch (error) {
    console.error('Error processing suppression reminders:', error);
  }
}

// Example usage
function main(): void {
  // Simulate lint results with suppressed errors
  const lintResults: LintResult[] = [
    {
      filePath: 'example.js',
      suppressedErrors: [
        { ruleId: 'no-console', line: 1, column: 1 },
        { ruleId: 'no-unused-vars', line: 2, column: 2 },
      ],
    },
  ];

  remindSuppressions(lintResults);

  // Print the updated lint results
  console.log(lintResults);
}

main();