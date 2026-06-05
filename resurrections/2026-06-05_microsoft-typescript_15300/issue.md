# Index signature is missing in type (only on interfaces, not on type alias)

**Repository:** [microsoft/TypeScript](https://github.com/microsoft/TypeScript)
**Issue:** [microsoft/TypeScript#15300](https://github.com/microsoft/TypeScript/issues/15300)
**Reactions:** 367 👍
**Created:** 2017-04-21T00:29:53Z
**Last Activity:** 2022-11-18T22:55:09Z
**Labels:** Suggestion, In Discussion

---

## Original Description

**TypeScript Version:**  2.2.2

**Code**

```ts
interface IndexType {
     [key: string]: string;
}

interface doesNotWork {
    hola: string;
}
type doWorks = { hola: string };

let y: IndexType;

const correctA = { hola: "hello" };
const correctB: doWorks = { hola: "hello" };
//error should be assignable to y
const error: doesNotWork = { hola: "hello " };

y = correctA;
y = correctB;
y = error; //Index signature is missing in type 'doesNotWork'
y = {... error}; //workaround but not equivalent since the instance is not the same
```

**Expected behavior:**
The code should not result on a compiler error since the interface `doesNotWork` is equivalent to the type `{ hola: string }`

**Actual behavior:**
Variable `error` of type `doesNotWork` can't be assigned to y

---

*Resurrected by Resurrection Bot 🧬*
