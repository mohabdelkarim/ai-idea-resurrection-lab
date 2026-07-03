interface TextMessage {
    type: 'text',
    text: string
}

interface ImageMessage {
    type: 'image',
    url: string
}

type Message = TextMessage | ImageMessage;

function isTextMessage(message: Message): message is TextMessage {
    return message.type === 'text';
}

function isTextMessageIncludes(message: Message): message is TextMessage {
    return ['text'].indexOf(message.type) > -1;
}

function isTextMessageIncludesOr(message: Message): message is TextMessage {
    return ['text', 'image'].includes(message.type);
}

function testMessage(message: Message) {
    if (isTextMessage(message)) {
        console.log(message.text);
    }
}

function testMessageIncludes(message: Message) {
    if (isTextMessageIncludes(message)) {
        console.log(message.text);
    }
}

function testMessageIncludesOr(message: Message) {
    if (isTextMessageIncludesOr(message)) {
        if (message.type === 'text') {
            console.log(message.text);
        } else {
            console.log(message.url);
        }
    }
}

try {
    const message: Message = { type: 'text', text: 'Hello World' };
    testMessage(message);
    testMessageIncludes(message);
    testMessageIncludesOr(message);
} catch (error) {
    console.error(error);
}