package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/hashicorp/cli"
	"github.com/hashicorp/terraform/internal/legacy"
	"github.com/hashicorp/terraform/internal/tfdiags"
)

func main() {
	args := os.Args[1:]
	if len(args) < 1 {
		log.Fatal("missing command")
	}

	cmd := args[0]
	switch cmd {
	case "plan":
		plan(args[1:])
	case "apply":
		apply(args[1:])
	default:
		log.Fatalf("unknown command %q", cmd)
	}
}

func plan(args []string) {
	flag.Usage = func() {
		fmt.Println("Usage: terraform plan [options]")
		fmt.Println("Options:")
		fmt.Println("  -out=FILE   Output plan to the given file")
	}

	var outFile string
	flag.StringVar(&outFile, "out", "", "output plan file")
	flag.Parse()

	if flag.NArg() != 0 {
		log.Fatal("unexpected arguments")
	}

	// Simulate a plan that may require partial application
	plan, err := simulatePlan()
	if err != nil {
		log.Fatal(err)
	}

	if outFile != "" {
		f, err := os.Create(outFile)
		if err != nil {
			log.Fatal(err)
		}
		defer f.Close()

		enc := json.NewEncoder(f)
		enc.SetIndent("", "  ")
		if err := enc.Encode(plan); err != nil {
			log.Fatal(err)
		}
	} else {
		fmt.Println("Plan:")
		fmt.Printf("%#v\n", plan)
	}
}

func apply(args []string) {
	flag.Usage = func() {
		fmt.Println("Usage: terraform apply [options] [plan file]")
	}

	flag.Parse()

	if flag.NArg() != 1 {
		log.Fatal("exactly one argument expected")
	}

	planFile := flag.Arg(0)
	f, err := os.Open(planFile)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	var plan map[string]interface{}
	dec := json.NewDecoder(f)
	if err := dec.Decode(&plan); err != nil {
		log.Fatal(err)
	}

	// Simulate applying the plan
	err = simulateApply(plan)
	if err != nil {
		log.Fatal(err)
	}
}

func simulatePlan() (map[string]interface{}, error) {
	// This is a very simplified example of a plan that may require partial application
	plan := map[string]interface{}{
		"resources": []map[string]interface{}{
			{
				"name":  "example",
				"type":  "example",
				"state": "pending",
			},
		},
	}

	// Randomly decide if this plan requires partial application
	if rand.Intn(2) == 0 {
		plan["partial"] = true
	}

	return plan, nil
}

func simulateApply(plan map[string]interface{}) error {
	// This is a very simplified example of applying a plan
	if partial, ok := plan["partial"]; ok && partial.(bool) {
		fmt.Println("Plan requires partial application")
		// Return a special error to indicate that partial application is required
		return errors.New("partial application required")
	}

	fmt.Println("Applying plan...")
	return nil
}