# Spawning editors

**Repository:** [charmbracelet/bubbletea](https://github.com/charmbracelet/bubbletea)
**Issue:** [charmbracelet/bubbletea#171](https://github.com/charmbracelet/bubbletea/issues/171)
**Reactions:** 5 👍
**Created:** 2021-12-13T19:30:46Z
**Last Activity:** 2022-04-12T18:14:43Z
**Labels:** enhancement

---

## Original Description

Hi,

Thanks for the awesome project!

Question: how to properly start subcommand with reuse of Stdout/Stdin?

I'm doing it like so:
https://github.com/antonmedv/llama/blob/58c042eb06a5a661a1388beb4ac09cedf2764ad0/main.go#L183-L190
```go
func (m *model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	if m.editMode {
		return m, nil
	}
```
```go
				cmd := exec.Command(lookup([]string{"LLAMA_EDITOR", "EDITOR"}, "less"), filepath.Join(m.path, m.cursorFileName()))
				cmd.Stdin = os.Stdin
				cmd.Stdout = os.Stdout
				// Note: no Stderr as redirect `llama 2> /tmp/path` can be used.
				m.editMode = true
				_ = cmd.Run()
				m.editMode = false
				return m, tea.HideCursor
```
But what to do if a redraw is needed after cmd exits?  And is there a better way to halt the program until cmd is exited? 

Thanks.

_Originally posted by @antonmedv in https://github.com/charmbracelet/bubbletea/discussions/170_

---

*Resurrected by Resurrection Bot 🧬*
