
// Import the necessary libraries
import { Capnp } from 'capnp-ts';
import { MessageBroker } from './message-broker';

// Define the message structure
const message = Capnp.schema`
  struct Message {
    id @0 :UInt64;
    payload @1 :Text;
  }
`;

// Create a message broker instance
const broker = new MessageBroker();

// Define a function to send a message
async function sendMessage(id: number, payload: string) {
  // Create a new message
  const msg = new message.Message();
  msg.id = id;
  msg.payload = payload;

  // Send the message to the broker
  await broker.sendMessage(msg);
}

// Define a function to receive a message
async function receiveMessage() {
  // Receive a message from the broker
  const msg = await broker.receiveMessage();

  // Process the message
  console.log(`Received message with id ${msg.id} and payload ${msg.payload}`);
}

// Test the system
async function test() {
  // Send a message
  await sendMessage(1, 'Hello, world!');

  // Receive a message
  await receiveMessage();
}

// Run the test
test();
