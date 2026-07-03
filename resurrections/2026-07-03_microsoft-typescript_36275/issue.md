# .includes or .indexOf does not narrow the type

**Repository:** [microsoft/TypeScript](https://github.com/microsoft/TypeScript)
**Issue:** [microsoft/TypeScript#36275](https://github.com/microsoft/TypeScript/issues/36275)
**Reactions:** 55 👍
**Created:** 2020-01-18T00:40:03Z
**Last Activity:** 2025-04-14T12:47:40Z
**Labels:** Suggestion, Too Complex

---

## Original Description

<!-- 🚨 STOP 🚨 𝗦𝗧𝗢𝗣 🚨 𝑺𝑻𝑶𝑷 🚨

Half of all issues filed here are duplicates, answered in the FAQ, or not appropriate for the bug tracker. Even if you think you've found a *bug*, please read the FAQ first, especially the Common "Bugs" That Aren't Bugs section!

Please help us by doing the following steps before logging an issue:
  * Search: https://github.com/Microsoft/TypeScript/search?type=Issues
  * Read the FAQ: https://github.com/Microsoft/TypeScript/wiki/FAQ

Please fill in the *entire* template below.
-->

<!--
Please try to reproduce the issue with the latest published version. It may have already been fixed.
For npm: `typescript@next`
This is also the 'Nightly' version in the playground: http://www.typescriptlang.org/play/?ts=Nightly
-->
**TypeScript Version:**  3.7.x-dev.201xxxxx

<!-- Search terms you tried before logging this (so others can find this issue more easily) -->
**Search Terms:** `.includes type narrowing`, `.indexOf type narrowing`

**Code**

```ts
interface TextMessage {
    type: 'text',
    text: string
}

interface ImageMessage {
    type: 'image',
    url: string
}

type Message = TextMessage | ImageMessage;

// This is an example to reproduce the error in Playground.
// In practice, assume this message comes from outside our control (e.g. HTTP request)
const message: Message = JSON.parse(prompt('') as string) as Message;

if (message.type === 'text') {
    // No error here
    message.text = message.text.trim();
}

// Same for ['text'].includes(message.type)
if (['text'].indexOf(message.type) > -1) {
    // Error: Property 'text' does not exist on type 'ImageMessage'
    message.text = message.text.trim();
}
```

**Expected behavior:**
I expect `message` to narrow its type to `TextMessage` inside `if (['text'].indexOf(message.type) > -1)`.

Same way it does inside `if (message.type === 'text')`

**Actual behavior:**
`message` is typed as `TextMessage | ImageMessage` inside the `if` block
```ts
if (['text'].indexOf(message.type) > -1) {
    // Error: Property 'text' does not exist on type 'ImageMessage'
    message.text = message.text.trim();
}
```

**Playground Link:** [Provided](https://www.typescriptlang.org/play/?target=1&module=5#code/JYOwLgpgTgZghgYwgAgCoQB5gLIQM55wDmKA3gFDJXJgCeADhAFzIDkkWrANJdR2CzxgooIuQC+5cqEixEKAJIBbYhFwFVyCtRoNmbYCpLdeVAK5QANoOGiJUuo2TrCJZAF40mHPlcoAPsjKqi6qANxSAPSRaAAWwHjICchwIMiYcEr0lihgAPbIUBD0UHkAJmZINLEo0KVQSWkACpZwtESlZiBlAHTk0UFpJYhgwEhcKQRmSrnxiTMabgh5C8gwpUrIeWZgeMBlKNsNy+CllsgAFBA9RD3IABKoqE2FEACOZvhgAJTkJ0LIBZ+FihNyeABSAGUAPIAOR69DgUDwEAuJRW9DAF1YrG+k2QQhEICIeLgiVBEAi0hglyBqh6jhQ7mZbH4uK0pmQA1hBTqeQaNSKnLpJAZ3g8gN89P4DJESgu3wikn6MUhmRQMH5yAA2uxvKwALo9UAISxmA54C4i66M37AGkXXVso2gA4YaEwK1S0W25AAPmQAFoAIx47TUAYAUSg9RYTVKjCgdFZ+uQZTy+GQIDyYHSGASubyaUZbGCJAprGF3pt4s81rFWFlhgVSqAA)

**Related Issues:** https://github.com/microsoft/TypeScript/issues/9842

My argument is that `if (message.type === 'text')` should be consid

---

*Resurrected by Resurrection Bot 🧬*
