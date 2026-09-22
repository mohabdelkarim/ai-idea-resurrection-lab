# Next 13: router.push with different searchParams does not trigger suspense fallback

**Repository:** [vercel/next.js](https://github.com/vercel/next.js)
**Issue:** [vercel/next.js#42346](https://github.com/vercel/next.js/issues/42346)
**Reactions:** 24 👍
**Created:** 2022-11-02T12:03:26Z
**Last Activity:** 2025-11-04T00:05:42Z
**Labels:** bug, locked, stale

---

## Original Description

### Verify canary release

- [X] I verified that the issue exists in the latest Next.js canary release

### Provide environment information

 Operating System:
      Platform: win32
      Arch: x64
      Version: Windows 10 Home
    Binaries:
      Node: 18.12.0
      npm: N/A
      Yarn: N/A
      pnpm: N/A
    Relevant packages:
      next: 13.0.2-canary.0
      eslint-config-next: 13.0.0
      react: 18.2.0
      react-dom: 18.2.0

### What browser are you using? (if relevant)

_No response_

### How are you deploying your application? (if relevant)

next dev

### Describe the Bug

 I'm struggling HARD with the `appDir Suspense` with `searchParams` . 

On **initial render**, the culprit falls back to the skeleton _just fine_. It's when I set **new searchParams** with `router.push` from another component, **the suspense fallback never renders**, and the server just **sits there** until data fetching gets completed.

**TL; DR, Changing searchParams does't make use of server-side suspense.** 

I'd greatly appreciate any help!


### Expected Behavior

The **`Foo` component**, 
_(i.e., the async server component that re-fetches data on prop change triggered by new searchParams acquired via the next router,)_ 
**when given new searchParams** --- thusly fetches new data --- should **fallback to the suspense's fallback component** _(e.g., a skeleton component)._

### Link to reproduction

https://github.com/krsteve/next-13-searchparam-bug

### To Reproduce

Code that DOES REPRODUCE the problem:

`page.tsx`
```tsx
import { Suspense } from "react";
import Foo from "./Foo";

export default function ({ searchParams }: { searchParams: { foo?: string } }) {
    return <Suspense fallback={<div>LOADING</div>}>
        {/* @ts-ignore */}
        <Foo foo={searchParams.foo} />
    </Suspense>;
}
```


`Foo.tsx`
```tsx
import { Button } from "./Button";

export default async function ({ foo }: { foo?: string }) {
    // Wait 3 seconds
    await new Promise(resolve => setTimeout(resolve, 3000));
    return <div>
        <div>{foo ?? "No Params"}</div>
        <Button />
    </div>;
}
```


`Button.tsx`
```tsx
'use client';

import { usePathname, useRouter } from "next/navigation";
import type { FC } from "react";

export const Button: FC = () => {
    const router = useRouter();
    const pathname = usePathname();
    const randNum = Math.ceil(Math.random() * 100);
    const setNewParams = () => {
        router.push(pathname + `?foo=${randNum}`);
    }

    return <button onClick={setNewParams}>Set New Params</button>
}
```


- Using router.replace does the same thing.
- Adding loading.tsx doesn't make any difference.
- Manually navigating with window.location.href does work, but it's just another initial rendering. (Re-renders the whole thing.)

---

*Resurrected by Resurrection Bot 🧬*
