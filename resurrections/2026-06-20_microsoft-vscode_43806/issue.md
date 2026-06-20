# Allow custom setting/control of workbench tab titles

**Repository:** [microsoft/vscode](https://github.com/microsoft/vscode)
**Issue:** [microsoft/vscode#43806](https://github.com/microsoft/vscode/issues/43806)
**Reactions:** 102 👍
**Created:** 2018-02-16T06:37:05Z
**Last Activity:** 2024-07-19T23:24:29Z
**Labels:** feature-request, info-needed, workbench-tabs

---

## Original Description

Hi there,

In my project, I have files with quite long file names (beyond my control).  This limits me to having 3-4 tabs show in my workbench at once.  I would like to be able to rename these tabs, or control their label format myself, in order to have more condense tab titles and thus more easily navigate my tabs.  This was roughly suggested by #21662 but was not really addressed by #12965 -- any of the options for `workbench.editor.labelFormat` still give me tab titles that are too long.  Can `workbench.editor.labelFormat` be modified, for example, to optionally take a formatter lambda function we can provide?  As just one example of a reasonable formatter one might write, it could be that you fix tab titles to 20 chars, and for long filenames you truncate and prepend with "...".  Additionally, one might want to assign nickname/shorthand tab titles for commonly used files.  Please pardon me if there is already a way to do this (would love to know how!), but if not, I'd sincerely appreciate considering this as a feature request.

Thanks!

---

*Resurrected by Resurrection Bot 🧬*
