import { appWindow } from '@tauri-apps/api/window';
import { invoke } from '@tauri-apps/api/tauri';

// Initialize Tauri app
invoke('init_app').then((response) => {
  console.log('Tauri app initialized:', response);
}).catch((error) => {
  console.error('Error initializing Tauri app:', error);
});

// Create a new window
const createWindow = async () => {
  try {
    const window = await appWindow.create({
      title: 'VSCode Tauri Proof of Concept',
      width: 800,
      height: 600,
    });
    console.log('Window created:', window);
  } catch (error) {
    console.error('Error creating window:', error);
  }
};

// Handle incoming messages from the Rust core
invoke('listen_message').then((response) => {
  console.log('Received message from Rust core:', response);
}).catch((error) => {
  console.error('Error listening for messages:', error);
});

// Send a message to the Rust core
const sendMessage = async () => {
  try {
    const response = await invoke('send_message', { message: 'Hello from TypeScript!' });
    console.log('Message sent to Rust core:', response);
  } catch (error) {
    console.error('Error sending message:', error);
  }
};

// Call the functions
createWindow();
sendMessage();

// Error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});

process.on('unhandledRejection', (reason) => {
  console.error('Unhandled rejection:', reason);
});