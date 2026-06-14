# feat: better RAG

**Repository:** [open-webui/open-webui](https://github.com/open-webui/open-webui)
**Issue:** [open-webui/open-webui#1293](https://github.com/open-webui/open-webui/issues/1293)
**Reactions:** 70 👍
**Created:** 2024-03-25T11:04:54Z
**Last Activity:** 2025-02-16T01:39:22Z
**Labels:** enhancement, good first issue, help wanted, core

---

## Original Description

**Is your feature request related to a problem? Please describe.**

The document-based RAG feature shows a glimpse of how useful it can be. Unfortunately for most practical applications, data is not sitting in a single self contained file:

- Source code repos span multiple files
- Cloud services like Jira, GitHub, Wordpress, Slack, etc. have REST APIs/webhooks and exporting data to a flat file is clunky and not always possible
- Structured data sources like MySQL or MongoDB databases

**Describe the solution you'd like**
- Generalize the Documents tab to Data Sources
- Keep the Document option as a Data Source
- Allow a Folder to be a Data Source, and recursively include all its containing files
- Allow for an API connector to connect common cloud tools like Slack, Jira, GitHub, Notion
- Allow for database connectors like MySQL, MongoDB so folks can enter a connection string and access the data
- Allow for generic REST API so folks can connect their own services

**Describe alternatives you've considered**
- Exporting from the sources to a flat file, then uploading the flat file

**Additional context**
- Happy to help if the team decides to do this
- Better to do it one step at a time, since each new Data Source adds incremental value to the tool

---

*Resurrected by Resurrection Bot 🧬*
