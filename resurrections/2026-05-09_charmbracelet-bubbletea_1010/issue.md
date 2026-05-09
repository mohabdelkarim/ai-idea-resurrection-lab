# Proposal: Model v2, program context

**Repository:** [charmbracelet/bubbletea](https://github.com/charmbracelet/bubbletea)
**Issue:** [charmbracelet/bubbletea#1010](https://github.com/charmbracelet/bubbletea/issues/1010)
**Reactions:** 13 👍
**Created:** 2024-05-09T17:08:39Z
**Last Activity:** 2024-08-28T18:11:39Z
**Labels:** proposal

---

## Original Description

During the execution of the program, models need to access the underlying terminal features and capabilities. We can achieved this with an API change that introduces Bubble Tea `Context`s. The nice thing about this `Context` type is that it can be used to control executions of goroutines because it embeds `context.Context`. Using `tea.WithContext(ctx)`, users can access the provided context before running the program in their Bubble Tea model.

# Bubble Tea Model Context

This fixes all sorts of issues with input and color, particularly in Wish. Basically, apps built on Bubble Tea v2 will “just work” if put behind a Wish server.

This also means that Bubble Tea now has first-class Lip Gloss support. Now, with the new advanced input handler, Bubble Tea can read and parse any type of sequence events as the terminal input buffer receive them.
This means that important events that can change the look and behavor of our program can be detected in Bubble Tea. When the program starts, it will query the terminal for Kitty Keyboard support and
the current terminal's background color. The background color is important because it affects Lip Gloss styles.

You can now use the new `tea.Context` to read different terminal capabilities. Bubble Tea now does all the heavy lifting of detecting terminal colors and background and can create `ctx.NewStyle()` that are
specific to the current running program (whether local or in a remote session). This will also pave the road for future improvements to be added on the context.

The new interface will look like this:

```go
// Model contains the program's state as well as its core functions.
type Model interface {
	// Init is the first function that will be called. It returns an optional
	// initial command. To not perform an initial command return nil.
	Init(ctx Context) (Model, Cmd)

	// Update is called when a message is received. Use it to inspect messages
	// and, in response, update the model and/or send a command.
	Update(ctx Context, msg Msg) (Model, Cmd)

	// View renders the program's UI, which is just a string. The view is
	// rendered after every Update.
	View(ctx Context) string
}

// Context represents a Bubble Tea program's context. It is passed to the
// program's Init, Update, and View functions to provide information about the
// program's state and to allow them to interact with the terminal.
type Context interface {
	context.Context

	// BackgroundColor returns the current background color of the terminal.
	// It returns nil if the terminal's doesn't support querying the background
	// color.
	BackgroundColor() color.Color

	// HasLightBackground returns true if the terminal's background color is
	// light. This is useful for determining whether to use light or dark colors
	// in the program's UI.
	HasLightBackground() bool

	// SupportsEnhancedKeyboard reports whether the terminal supports enhanced
	// keyboard keys. On Windows, this means it supports

---

*Resurrected by Resurrection Bot 🧬*
