# eslint-plugin-react-hooks & "Flat Config" (ESLint 9)

**Repository:** [facebook/react](https://github.com/facebook/react)
**Issue:** [facebook/react#28313](https://github.com/facebook/react/issues/28313)
**Reactions:** 238 👍
**Created:** 2024-02-13T14:14:11Z
**Last Activity:** 2025-03-23T00:14:27Z
**Labels:** Component: ESLint Rules

---

## Original Description

👋 Coming over from https://github.com/eslint/eslint/issues/18093: ESLint is migrating to a [new "flat config" format](https://eslint.org/docs/latest/use/configure/configuration-files-new) that will be the default in ESLint v9.

It doesn't look like `eslint-plugin-react-hooks` has documented support yet. But, based on searching around (e.g. https://github.com/vercel/next.js/discussions/49337), ESLint v9 is _basically_ supported if you wire it up manually in your config:

```js
// eslint.config.js
import eslint from "@eslint/js";
import hooksPlugin from "eslint-plugin-react-hooks";

export default [
  eslint.configs.recommended,
  {
    plugins: {
      "react-hooks": hooksPlugin,
    },
    rules: hooksPlugin.configs.recommended.rules,
  },
];
```

Most community plugins provide a more convenient wrapper. For example, [`eslint-plugin-jsdoc`](https://github.com/gajus/eslint-plugin-jsdoc?tab=readme-ov-file#flat-config) provides a `jsdoc.configs['flat/recommended']` object:

```js
// eslint.config.js
import jsdoc from 'eslint-plugin-jsdoc';

export default [
  jsdoc.configs['flat/recommended'],
];
```

Would the React team be open to a PR adding in a preset object like that? And either way, updating the docs on https://www.npmjs.com/package/eslint-plugin-react-hooks?

Note: this was also filed as https://github.com/reactjs/react.dev/issues/6430.

I'm posting this issue here as a reference & cross-linking it to the table in https://github.com/eslint/eslint/issues/18093. If there's anything technical blocking the extension from working with flat configs, please let us know - we'd be happy to try to help! 💜 

Additional resources:
* [Configuration Migration Guide](https://eslint.org/docs/latest/use/configure/migration-guide)
* _(edit)_ [Plugin Migration Guide](https://eslint.org/docs/latest/extend/plugin-migration-flat-config)
* Blog posts on the new config system: [Part 1: Background](https://eslint.org/blog/2022/08/new-config-system-part-1/), [Part 2: Introduction to flat config](https://eslint.org/blog/2022/08/new-config-system-part-2/)

_(sorry for not using the issue templates - I wasn't sure whether this would count as a bug)_

---

*Resurrected by Resurrection Bot 🧬*
