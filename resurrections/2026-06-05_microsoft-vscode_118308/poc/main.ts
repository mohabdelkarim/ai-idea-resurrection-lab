import { appWindow } from '@tauri-apps/api/window';
import { invoke } from '@tauri-apps/api/tauri';

// Define a Tauri-compatible wrapper for the VSCode extension API
class VscodeExtensionApi {
  async init() {
    try {
      // Initialize the extension API
      await invoke('init_extension_api');
    } catch (error) {
      console.error('Error initializing extension API:', error);
    }
  }

  async executeCommand(command: string, ...args: any[]) {
    try {
      // Execute a command using the extension API
      return await invoke('execute_command', { command, args });
    } catch (error) {
      console.error('Error executing command:', error);
    }
  }
}

// Create a new instance of the VSCode extension API wrapper
const vscodeApi = new VscodeExtensionApi();

// Initialize the extension API
vscodeApi.init().then(() => {
  console.log('Extension API initialized');
}).catch((error) => {
  console.error('Error initializing extension API:', error);
});

// Define a sample extension command
async function sampleCommand() {
  try {
    // Execute the sample command using the extension API
    const result = await vscodeApi.executeCommand('sampleCommand');
    console.log('Sample command result:', result);
  } catch (error) {
    console.error('Error executing sample command:', error);
  }
}

// Call the sample command
sampleCommand().then(() => {
  console.log('Sample command executed');
}).catch((error) => {
  console.error('Error executing sample command:', error);
});

// Handle window events
appWindow.listen('tauri://close-requested', () => {
  // Handle window close request
  console.log('Window close requested');
});

appWindow.listen('tauri://resized', (event) => {
  // Handle window resize
  console.log('Window resized:', event);
});