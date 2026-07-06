import * as vscode from 'vscode';

class NestedSnippetManager {
  private snippetStack: string[] = [];
  private maxDepth: number;

  constructor(maxDepth: number = 5) {
    this.maxDepth = maxDepth;
  }

  public async expandSnippet(snippet: string, context: vscode.ExtensionContext): Promise<string> {
    try {
      this.snippetStack.push(snippet);
      if (this.snippetStack.length > this.maxDepth) {
        throw new Error(`Maximum nested snippet depth exceeded (${this.maxDepth}).`);
      }
      const expandedSnippet = await this.parseSnippet(snippet, context);
      this.snippetStack.pop();
      return expandedSnippet;
    } catch (error) {
      console.error('Error expanding snippet:', error);
      return snippet;
    }
  }

  private async parseSnippet(snippet: string, context: vscode.ExtensionContext): Promise<string> {
    const snippetRegex = /{{snippet:([^{}]+)}}/g;
    let match: RegExpExecArray | null;
    let expandedSnippet = snippet;
    while ((match = snippetRegex.exec(snippet)) !== null) {
      const snippetName = match[1].trim();
      const nestedSnippet = await this.getSnippet(snippetName, context);
      if (nestedSnippet) {
        expandedSnippet = expandedSnippet.replace(match[0], await this.expandSnippet(nestedSnippet, context));
      }
    }
    return expandedSnippet;
  }

  private async getSnippet(snippetName: string, context: vscode.ExtensionContext): Promise<string | undefined> {
    const snippets = await vscode.snippets.getSnippets(context);
    for (const snippet of snippets) {
      if (snippet.name === snippetName) {
        return snippet.body;
      }
    }
    return undefined;
  }
}

// Example usage:
vscode.commands.registerCommand('nested-snippets.expand', async () => {
  const snippet = 'Hello, {{snippet: greeting}}!';
  const context = vscode.ExtensionContext;
  const manager = new NestedSnippetManager();
  const expandedSnippet = await manager.expandSnippet(snippet, context);
  console.log(expandedSnippet);
});