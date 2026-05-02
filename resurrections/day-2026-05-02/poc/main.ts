/**
 * Proof of Concept: Git status in File Explorer
 * VS Code Extension — shows git status decorations on files in the explorer
 *
 * Prerequisites: Node.js 20+, VS Code Extension API
 * Run: npm install && npm run compile
 */
import * as vscode from 'vscode';
import { execSync } from 'child_process';
import * as path from 'path';

// Map git status letters to human-readable labels and badge chars
const STATUS_MAP: Record<string, { badge: string; tooltip: string; color: vscode.ThemeColor }> = {
  M: { badge: 'M', tooltip: 'Modified', color: new vscode.ThemeColor('gitDecoration.modifiedResourceForeground') },
  A: { badge: 'A', tooltip: 'Added', color: new vscode.ThemeColor('gitDecoration.addedResourceForeground') },
  D: { badge: 'D', tooltip: 'Deleted', color: new vscode.ThemeColor('gitDecoration.deletedResourceForeground') },
  '?': { badge: '?', tooltip: 'Untracked', color: new vscode.ThemeColor('gitDecoration.untrackedResourceForeground') },
};

class GitStatusDecorationProvider implements vscode.FileDecorationProvider {
  private _onDidChange = new vscode.EventEmitter<vscode.Uri | vscode.Uri[]>();
  readonly onDidChangeFileDecorations = this._onDidChange.event;

  private statusMap = new Map<string, string>();

  constructor() {
    this.refresh();
  }

  refresh(): void {
    this.statusMap.clear();
    try {
      const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
      if (!workspaceRoot) return;

      const output = execSync('git status --porcelain', {
        cwd: workspaceRoot,
        encoding: 'utf8',
      });

      for (const line of output.split('\n')) {
        if (!line.trim()) continue;
        const statusChar = line[0] !== ' ' ? line[0] : line[1];
        const filePath = line.slice(3).trim();
        const absPath = path.join(workspaceRoot, filePath);
        this.statusMap.set(absPath, statusChar);
      }
    } catch {
      // Not a git repo or git not installed — silently skip
    }
    this._onDidChange.fire(undefined as unknown as vscode.Uri);
  }

  provideFileDecoration(uri: vscode.Uri): vscode.FileDecoration | undefined {
    const status = this.statusMap.get(uri.fsPath);
    if (!status) return undefined;
    const info = STATUS_MAP[status];
    if (!info) return undefined;
    return {
      badge: info.badge,
      tooltip: info.tooltip,
      color: info.color,
      propagate: true,
    };
  }
}

export function activate(context: vscode.ExtensionContext): void {
  const provider = new GitStatusDecorationProvider();
  context.subscriptions.push(
    vscode.window.registerFileDecorationProvider(provider)
  );

  // Refresh decorations when files change
  const watcher = vscode.workspace.createFileSystemWatcher('**/*');
  context.subscriptions.push(
    watcher.onDidChange(() => provider.refresh()),
    watcher.onDidCreate(() => provider.refresh()),
    watcher.onDidDelete(() => provider.refresh()),
    watcher
  );

  // Manual refresh command
  context.subscriptions.push(
    vscode.commands.registerCommand('gitStatusExplorer.refresh', () => provider.refresh())
  );
}

export function deactivate(): void {}
