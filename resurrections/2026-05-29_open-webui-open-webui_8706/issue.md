# Better <think> block rendering for DeepSeek-R1 and similar

**Repository:** [open-webui/open-webui](https://github.com/open-webui/open-webui)
**Issue:** [open-webui/open-webui#8706](https://github.com/open-webui/open-webui/issues/8706)
**Reactions:** 76 👍
**Created:** 2025-01-21T03:38:37Z
**Last Activity:** 2025-02-25T15:50:17Z
**Labels:** 

---

## Original Description

**Is your feature request related to a problem? Please describe.**  
Currently, when reasoning LLMs return a `<think>` block as part of their output, it is rendered in the same way as regular text responses… just surrounded by the unfortunate <think> tags. This makes it difficult to visually distinguish between the reasoning process and the final answer. Additionally, lengthy `<think>` blocks can clutter the interface and reduce readability for users who primarily want to focus on the final output.

**Describe the solution you'd like**  
I propose that the `<think>` block be rendered distinctly from the normal response, with a visual differentiation (e.g., a shaded background, a border, or an indented box). Furthermore, the `<think>` block should be collapsible, allowing users to expand or hide it as needed. By default, the block could be collapsed, with an indicator to expand it for users who are interested in understanding the detailed reasoning process.

**Describe alternatives you've considered**  
1. Using a toggle option in the settings to enable or disable `<think>` block rendering entirely. 
2. Highlighting `<think>` blocks with simple visual markers (e.g., italics or a different font) instead of full collapsibility.

**Additional context**  
This enhancement would make the UI more user-friendly, especially for users who want a clean response while still having the option to delve into the reasoning when needed. Here’s a simple example mockup of how it might look:

- Collapsed `<think>` block: `[+] Reasoning available. Click to expand.`  
- Expanded `<think>` block: A visually distinct, bordered box containing the detailed reasoning.


---

*Resurrected by Resurrection Bot 🧬*
