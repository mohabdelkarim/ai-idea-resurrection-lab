import * as vscode from 'vscode';
const gitStatusDecorator = (context: vscode.ExtensionContext) => {
  const provider = new vscode.TreeDataProvider<vscode.FileDecoration>();
  provider.onDidChangeTreeData(() => context.globalState.change(event));
  context.subscriptions.push(vscode.window.registerTreeDataProvider('gitStatus', provider));
};
export function activate(context: vscode.ExtensionContext) {
  gitStatusDecorator(context);
}
export function deactivate() {}
