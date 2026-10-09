# Support multiple formatters for a single file

**Repository:** [microsoft/vscode](https://github.com/microsoft/vscode)
**Issue:** [microsoft/vscode#142904](https://github.com/microsoft/vscode/issues/142904)
**Reactions:** 90 👍
**Created:** 2022-02-12T05:54:21Z
**Last Activity:** 2023-02-23T12:24:47Z
**Labels:** feature-request, formatting, *out-of-scope

---

## Original Description

<!-- ⚠️⚠️ Do Not Delete This! feature_request_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- Please search existing issues to avoid creating duplicates. -->

Back in 2019, #84603 was opened to request multiple formatter support. I would like to re-open this request again. Having multiple formatters is quite common in the modern toolchain and the lack of support for this in VS Code makes it very frustrating to use. The suggestion proposed was to allow an array of values for `editor.defaultFormatter` which would run each formatter in the order specified, eg:

```json
"[typescript]": {
    "editor.defaultFormatter": ["esbenp.prettier-vscode", "publisher.some-other-formatter"]
}
```

Some common scenarios where this would be helpful:

- JavaScript/TypeScript code that uses both Prettier and ESLint. ESLint already supports tight integration with Prettier via `eslint-plugin-prettier` and other editors (like Atom) handle them both auto-formatting code on file save properly
- CSS code that uses both Stylelint and Prettier. This is another common scenario. In this case you let Prettier handle the formatting changes, and let Stylelint handle all other linting. Both support auto-fixing of files.

Having to choose only one formatter leads to complex interactions between them (eg. https://github.com/microsoft/vscode-eslint/issues/1417). I think allowing multiple formatters to run in sequence would address a lot of friction and would eliminate the need to force users to select a default formatter entirely.

---

*Resurrected by Resurrection Bot 🧬*
