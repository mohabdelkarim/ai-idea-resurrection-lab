// Proof of concept: CSI-u (Kitty keyboard protocol) support in Bubble Tea
// Demonstrates how an extended key event would flow through the real tea.Msg system.
// Uses ONLY stdlib — no external deps required to run.
// Run: go run main.go   (then press keys; Ctrl+C to quit)
package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"

	"golang.org/x/term"
)

// ---------------------------------------------------------------------------
// KeyMsg mirrors what bubbletea's tea.KeyMsg would look like with CSI-u.
// In a real PR this struct would extend charmbracelet/bubbletea's KeyMsg.
// ---------------------------------------------------------------------------

type KeyType int

const (
	KeyRune    KeyType = iota
	KeyUnknown         // existing bubbletea sentinel
	// CSI-u adds modifier-aware variants:
	KeyCtrlShiftA
	KeyCtrlShiftB
	// ... full table would live in keys.go
)

type Modifiers uint8

const (
	ModShift Modifiers = 1 << iota
	ModAlt
	ModCtrl
)

// KeyMsg is the extended version that carries modifier bits and Unicode codepoint.
type KeyMsg struct {
	Type      KeyType
	Runes     []rune
	Modifiers Modifiers
	Alt       bool // kept for back-compat with existing bubbletea API
}

func (k KeyMsg) String() string {
	var parts []string
	if k.Modifiers&ModCtrl != 0 {
		parts = append(parts, "ctrl")
	}
	if k.Modifiers&ModShift != 0 {
		parts = append(parts, "shift")
	}
	if k.Modifiers&ModAlt != 0 {
		parts = append(parts, "alt")
	}
	if len(k.Runes) > 0 {
		parts = append(parts, string(k.Runes))
	}
	return strings.Join(parts, "+")
}

// ---------------------------------------------------------------------------
// CSI-u parser — would live in internal/input.go in the real bubbletea PR.
// Sequence format: ESC [ <unicode> ; <modifiers> u
// ---------------------------------------------------------------------------

func parseCSIu(seq string) (KeyMsg, bool) {
	// seq arrives WITHOUT the leading ESC[
	// example: "65;5u" = 'A' (65) with Ctrl+Shift (modifiers=5)
	if !strings.HasSuffix(seq, "u") {
		return KeyMsg{}, false
	}
	seq = strings.TrimSuffix(seq, "u")
	parts := strings.SplitN(seq, ";", 2)

	codepoint, err := strconv.Atoi(parts[0])
	if err != nil || codepoint < 1 {
		return KeyMsg{}, false
	}

	var mods Modifiers
	if len(parts) == 2 {
		modInt, err := strconv.Atoi(parts[1])
		if err == nil {
			// CSI-u modifier encoding: value = modifier_mask + 1
			modMask := modInt - 1
			if modMask&1 != 0 {
				mods |= ModShift
			}
			if modMask&2 != 0 {
				mods |= ModAlt
			}
			if modMask&4 != 0 {
				mods |= ModCtrl
			}
		}
	}

	return KeyMsg{
		Type:      KeyRune,
		Runes:     []rune{rune(codepoint)},
		Modifiers: mods,
		Alt:       mods&ModAlt != 0,
	}, true
}

// ---------------------------------------------------------------------------
// readKey reads one key event from a raw-mode terminal.
// In bubbletea this lives in the input reader goroutine that produces tea.Msg.
// ---------------------------------------------------------------------------

func readKey(r *bufio.Reader) (KeyMsg, error) {
	b, err := r.ReadByte()
	if err != nil {
		return KeyMsg{}, err
	}

	// ESC sequence
	if b == 0x1b {
		next, err := r.ReadByte()
		if err != nil || next != '[' {
			return KeyMsg{Type: KeyUnknown}, nil
		}
		// Read until we find a final byte (alphabetic)
		var sb strings.Builder
		for {
			c, err := r.ReadByte()
			if err != nil {
				break
			}
			sb.WriteByte(c)
			if c >= 0x40 && c <= 0x7E { // final byte range
				break
			}
		}
		if msg, ok := parseCSIu(sb.String()); ok {
			return msg, nil
		}
		return KeyMsg{Type: KeyUnknown}, nil
	}

	// Plain rune
	return KeyMsg{Type: KeyRune, Runes: []rune{rune(b)}}, nil
}

// ---------------------------------------------------------------------------
// Minimal Bubble Tea-style update loop.
// In real bubbletea the Program.Start() loop calls Update(msg tea.Msg).
// This demo shows exactly that integration point.
// ---------------------------------------------------------------------------

type Model struct {
	keys []string
	quit bool
}

func update(m Model, msg KeyMsg) Model {
	if msg.Type == KeyRune && len(msg.Runes) > 0 && msg.Runes[0] == 'q' {
		m.quit = true
		return m
	}
	m.keys = append(m.keys, msg.String())
	if len(m.keys) > 10 {
		m.keys = m.keys[len(m.keys)-10:]
	}
	return m
}

func view(m Model) string {
	var sb strings.Builder
	sb.WriteString("\033[H\033[2J") // clear screen
	sb.WriteString("CSI-u keyboard PoC — press keys (q to quit)\n\n")
	for _, k := range m.keys {
		sb.WriteString("  " + k + "\n")
	}
	return sb.String()
}

func main() {
	// Put terminal in raw mode so we receive escape sequences unprocessed.
	oldState, err := term.MakeRaw(int(os.Stdin.Fd()))
	if err != nil {
		// Graceful fallback if not a real terminal (e.g. piped input)
		fmt.Fprintln(os.Stderr, "not a terminal; running in demo mode")
		fmt.Println(parseCSIu("65;5u")) // demo: Ctrl+Shift+A
		return
	}
	defer term.Restore(int(os.Stdin.Fd()), oldState)

	reader := bufio.NewReader(os.Stdin)
	writer := io.Writer(os.Stdout)
	model := Model{}

	for !model.quit {
		fmt.Fprint(writer, view(model))
		msg, err := readKey(reader)
		if err != nil {
			break
		}
		model = update(model, msg)
	}

	fmt.Println("\nBye!")
}
