# Literal String Union Autocomplete

**Repository:** [microsoft/TypeScript](https://github.com/microsoft/TypeScript)
**Issue:** [microsoft/TypeScript#29729](https://github.com/microsoft/TypeScript/issues/29729)
**Reactions:** 245 👍
**Created:** 2019-02-04T17:44:40Z
**Last Activity:** 2025-01-08T18:47:50Z
**Labels:** Design Limitation

---

## Original Description

Autocomplete works for literal string unions, but adding a union of `string` negates autocomplete entirely. This has been brought up before but I believe there is enough value in this feature to be reconsidered.  

My use case is to have a union of string literals for several colors, but also allow hex codes without having to add 16.7 million string literals.

**TypeScript Version:**  3.4.0-dev.20190202

**Search Terms:** Literal string union autocomplete

**Code**

```ts
interface Options {
  borderColor: 'black' | 'red' | 'green' | 'yellow' | 'blue' | string
};

const opts: Options = {borderColor: 'red'};
```

**Expected behavior:**

![image](https://user-images.githubusercontent.com/11617455/52225250-918e1700-286f-11e9-8ed2-9ca7fe5b0b70.png)

**Actual behavior:**

![image](https://user-images.githubusercontent.com/11617455/52225328-bd110180-286f-11e9-8b5d-62d516c96564.png)

**Playground Link:** https://stackblitz.com/edit/typescript-bwyyab

**Related Issues:** #12687 #13614


---

*Resurrected by Resurrection Bot 🧬*
