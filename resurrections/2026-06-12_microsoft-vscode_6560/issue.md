# Allow to open different windows with different permissions

**Repository:** [microsoft/vscode](https://github.com/microsoft/vscode)
**Issue:** [microsoft/vscode#6560](https://github.com/microsoft/vscode/issues/6560)
**Reactions:** 129 👍
**Created:** 2016-05-19T22:53:19Z
**Last Activity:** 2024-12-08T14:40:04Z
**Labels:** feature-request, under-discussion, workbench-run-as-admin, *out-of-scope

---

## Original Description

- VSCode Version: 1.1.1
- OS Version: Windows 10 1511 (10586.318)

Steps to Reproduce:
1. Close all Code instances, then run Code as administrator (a new blank Code instance with administrator right)
2. In File Explorer, right click a text file and Open with Code, nothing will happen.

Note: there are multiple other ways to trigger this issue, the above repro is just an example.
Note 2: If you already have a code instance running without administrator running, the above issue will not get triggered. That's why the very first step is to close all Code instances.


---

*Resurrected by Resurrection Bot 🧬*
