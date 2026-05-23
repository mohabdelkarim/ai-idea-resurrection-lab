package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"time"

	"github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/ultraviolet"
	"github.com/lucasb-eyer/go-colorful"
)

type model struct {
	editMode bool
	editor   *exec.Cmd
}

func (m *model) Init() tea.Cmd {
	return nil
}

func (m *model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.String() == "ctrl+e" {
			if !m.editMode {
				m.editMode = true
				m.editor = exec.Command("less", "-")
				m.editor.Stdin = os.Stdin
				m.editor.Stdout = os.Stdout
				if err := m.editor.Start(); err != nil {
					log.Println(err)
					return m, nil
				}
				return m, tea.Halt
			} else {
				m.editMode = false
				if err := m.editor.Wait(); err != nil {
					log.Println(err)
				}
				return m, tea.ClearScreen
			}
	}
	return m, nil
}

func (m *model) View() string {
	if m.editMode {
		return ""
	}
	return "Press ctrl+e to enter edit mode"
}

func main() {
	m := &model{}
	p := bubbletea.NewProgram(m)
	if err := p.Start(); err != nil {
		log.Fatal(err)
	}
}