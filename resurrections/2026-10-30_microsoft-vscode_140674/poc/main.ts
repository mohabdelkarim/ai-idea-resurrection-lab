import * as vscode from 'vscode';

// Simple service that reads the new setting and updates the layout
class TabPlacementService {
    private readonly configurationKey = 'workbench.editor.tabPlacement';
    private readonly disposables: vscode.Disposable[] = [];
    private currentPlacement: 'top' | 'bottom' = 'top';

    constructor() {
        this.updatePlacement();
        // Listen to configuration changes
        this.disposables.push(vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration(this.configurationKey)) {
                this.updatePlacement();
            }
        }));
    }

    private updatePlacement() {
        const config = vscode.workspace.getConfiguration();
        const value = config.get<string>(this.configurationKey, 'top');
        if (value !== 'top' && value !== 'bottom') {
            console.error(`Invalid value for ${this.configurationKey}: ${value}. Falling back to 'top'.`);
            this.currentPlacement = 'top';
        } else {
            this.currentPlacement = value as 'top' | 'bottom';
        }
        this.applyPlacement();
    }

    private applyPlacement() {
        // In a real implementation we would move the TabBar component.
        // Here we just log the action for demonstration.
        console.log(`Applying tab placement: ${this.currentPlacement}`);
        // Example: add a CSS class to the workbench container
        const workbench = document.getElementById('workbench.main.container');
        if (!workbench) {
            console.warn('Workbench container not found.');
            return;
        }
        workbench.classList.remove('tabPlacementTop', 'tabPlacementBottom');
        workbench.classList.add(this.currentPlacement === 'top' ? 'tabPlacementTop' : 'tabPlacementBottom');
    }

    public dispose() {
        this.disposables.forEach(d => d.dispose());
    }
}

// Activate function for the extension
export function activate(context: vscode.ExtensionContext) {
    try {
        const service = new TabPlacementService();
        context.subscriptions.push(service);
        // Register a command to toggle placement for quick testing
        const toggleCmd = vscode.commands.registerCommand('extension.toggleTabPlacement', async () => {
            const config = vscode.workspace.getConfiguration();
            const current = config.get<string>('workbench.editor.tabPlacement', 'top');
            const newVal = current === 'top' ? 'bottom' : 'top';
            await config.update('workbench.editor.tabPlacement', newVal, vscode.ConfigurationTarget.Global);
            vscode.window.showInformationMessage(`Tab placement set to ${newVal}`);
        });
        context.subscriptions.push(toggleCmd);
    } catch (err) {
        console.error('Failed to activate TabPlacementService:', err);
    }
}

export function deactivate() {
    // Nothing to clean up – VS Code disposes subscriptions automatically
}