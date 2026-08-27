# Exclude files or directories from editor.formatOnSave

**Repository:** [microsoft/vscode](https://github.com/microsoft/vscode)
**Issue:** [microsoft/vscode#176946](https://github.com/microsoft/vscode/issues/176946)
**Reactions:** 91 👍
**Created:** 2023-03-13T09:58:38Z
**Last Activity:** 2025-05-04T18:11:25Z
**Labels:** feature-request, formatting, *out-of-scope

---

## Original Description

<!-- ⚠️⚠️ Do Not Delete This! feature_request_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- Please search existing issues to avoid creating duplicates. -->

<!-- Describe the feature you'd like. -->
Format on save should have an additional setting that allows the user to exclude files or directories based on some pattern from the format on save feature. This was requested in #147677, but closed as out of scope. @jrieken pointed out that you can disable format on save based on language, however that does not solve my problem. I work on large C++ projects, often with many third party dependencies. When modifying third party code, I would like to be able to save without applying my project-specific formatting to the thirdparty code. Being able to exclude directories from the editor.formatOnSave feature would solve this problem.


---

*Resurrected by Resurrection Bot 🧬*
