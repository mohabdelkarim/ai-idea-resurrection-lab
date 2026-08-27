import * as vscode from 'vscode';

// Register the new configuration schema (normally contributed via package.json, but added here for PoC)
function registerConfiguration() {
    const config = vscode.workspace.getConfiguration();
    // Ensure the setting exists; no schema registration at runtime, just a placeholder
    // Users can add "editor.formatOnSaveExclude": ["**/third_party/**"] to their settings.
}

// Helper to determine if a document should be excluded based on glob patterns
function isDocumentExcluded(document: vscode.TextDocument, excludePatterns: string[]): boolean {
    if (!excludePatterns || excludePatterns.length === 0) {
        return false;
    }
    const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
    const relativePath = workspaceFolder ? vscode.workspace.asRelativePath(document.uri) : document.fileName;
    // Use vscode's built‑in GlobPattern matcher via workspace.findFiles
    // Since findFiles is async, we create a temporary matcher function.
    for (const pattern of excludePatterns) {
        // The pattern may be absolute or relative; we use minimatch logic via vscode's API indirectly.
        // Simplify: use vscode.workspace.fs.stat to check match via glob-to-regexp conversion.
        // For PoC, perform a simple wildcard check.
        const regex = new RegExp('^' + pattern.replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*') + '$');
        if (regex.test(relativePath)) {
            return true;
        }
    }
    return false;
}

// Main function that sets up the format‑on‑save exclusion logic
export function activate(context: vscode.ExtensionContext) {
    try {
        registerConfiguration();
        const disposable = vscode.workspace.onWillSaveTextDocument(async (event) => {
            const config = vscode.workspace.getConfiguration('editor');
            const formatOnSave = config.get<boolean>('formatOnSave');
            if (!formatOnSave) {
                return; // Global formatOnSave disabled
            }
            const excludePatterns = config.get<string[]>('formatOnSaveExclude') || [];
            if (isDocumentExcluded(event.document, excludePatterns)) {
                // Skip formatting for this document
                return;
            }
            // Retrieve language‑specific formatOnSave setting
            const languageConfig = vscode.workspace.getConfiguration(`[${event.document.languageId}]`);
            const languageFormatOnSave = languageConfig.get<boolean>('editor.formatOnSave');
            if (languageFormatOnSave === false) {
                return; // Disabled for this language
            }
            // Invoke the built‑in formatting providers
            const edits = await vscode.commands.executeCommand<vscode.TextEdit[]>('vscode.executeFormatDocumentProvider', event.document.uri, {});
            if (edits && edits.length > 0) {
                event.waitUntil(Promise.resolve(edits));
            }
        });
        context.subscriptions.push(disposable);
    } catch (err) {
        console.error('Failed to activate formatOnSaveExclude extension:', err);
    }
}

export function deactivate() {
    // No cleanup needed for this PoC
}