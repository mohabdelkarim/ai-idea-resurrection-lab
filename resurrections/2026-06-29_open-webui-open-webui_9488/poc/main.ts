import { WebSocket } from 'ws';

class DeepseekR1Client {
  private ws: WebSocket;
  private url: string;

  constructor(url: string) {
    this.url = url;
    this.ws = new WebSocket(url);
  }

  public onMessage(callback: (message: string) => void): void {
    this.ws.on('message', (data) => {
      callback(data.toString());
    });
  }

  public onError(callback: (error: Error) => void): void {
    this.ws.on('error', (error) => {
      callback(error);
    });
  }

  public onClose(callback: () => void): void {
    this.ws.on('close', () => {
      callback();
    });
  }

  public sendMessage(message: string): void {
    this.ws.send(message);
  }
}

class OpenWebUI {
  private client: DeepseekR1Client;
  private thinkingSteps: string[];

  constructor(client: DeepseekR1Client) {
    this.client = client;
    this.thinkingSteps = [];
  }

  public connect(): void {
    this.client.onMessage((message) => {
      try {
        const data = JSON.parse(message);
        if (data.type === 'thinking_step') {
          this.thinkingSteps.push(data.step);
          this.renderThinkingSteps();
        } else if (data.type === 'final_result') {
          console.log('Final result:', data.result);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    });

    this.client.onError((error) => {
      console.error('Error occurred:', error);
    });

    this.client.onClose(() => {
      console.log('Connection closed');
    });
  }

  public renderThinkingSteps(): void {
    const thinkingStepsElement = document.getElementById('thinking-steps');
    if (thinkingStepsElement) {
      thinkingStepsElement.innerHTML = '';
      this.thinkingSteps.forEach((step) => {
        const stepElement = document.createElement('p');
        stepElement.textContent = step;
        thinkingStepsElement.appendChild(stepElement);
      });
    }
  }
}

const client = new DeepseekR1Client('ws://localhost:8080');
const openWebUI = new OpenWebUI(client);
openWebUI.connect();
client.sendMessage('start');