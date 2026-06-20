import * as vscode from 'vscode';

// Define a custom setting for workbench tab title format
vscode.Extensions.registerExtension('customTabTitle', () => {
  const disposable = vscode.Disposable.fn(() => { });
  const config = vscode.workspace.getConfiguration('workbench');
  const tabTitleFormatSetting = 'tab.titleFormat';

  // Define a default format function
  function defaultFormat(fileName: string): string {
    return fileName;
  }

  // Define a custom format function based on user setting
  function getCustomFormat(): (fileName: string) => string {
    const formatString = config.get<string>(tabTitleFormatSetting);
    if (formatString) {
      return (fileName: string) => {
        return formatString.replace('{fileName}', fileName);
      };
    } else {
      return defaultFormat;
    }
  }

  // Register a command to update tab title format
  const updateTabTitleFormatCmd = vscode.commands.registerCommand('customTabTitle.updateFormat', () => {
    const formatString = vscode.window.showInputBox({ prompt: 'Enter a custom format string (use {fileName} for file name)' });
    formatString.then((value) => {
      if (value) {
        config.update(tabTitleFormatSetting, value, vscode.ConfigurationTarget.User);
      }
    });
  });
  disposable.add(updateTabTitleFormatCmd);

  // Register a tab change listener to update tab title
  vscode.window.onDidChangeActiveTextEditor((editor) => {
    if (editor) {
      const fileName = editor.document.fileName;
      const customFormat = getCustomFormat();
      const tabTitle = customFormat(fileName);
      vscode.window.tabBar?.changeTabTitle(editor, tabTitle);
    }
  });

  return disposable;
});

// Error handling
try {
  // Activate the extension
  vscode.Extensions.onDidChange(() => { });
} catch (error) {
  console.error('Error activating extension:', error);
}