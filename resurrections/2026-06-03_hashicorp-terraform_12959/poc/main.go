package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/hashicorp/hcl/v2"
	"github.com/hashicorp/hcl/v2/hclparse"
)

func main() {
	if err := sortVariables(); err != nil {
		log.Fatal(err)
	}
}

func sortVariables() error {
	// Get the current working directory
	dir, err := os.Getwd()
	if err != nil {
		return err
	}

	// Walk through the directory and find variables.tf and terraform.tfvars files
	err = filepath.WalkDir(dir, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}

		if !d.IsDir() && (strings.HasSuffix(path, "variables.tf") || strings.HasSuffix(path, "terraform.tfvars")) {
			if err := sortFile(path); err != nil {
				return err
			}
		}
		return nil
	})
	return err
}

func sortFile(filePath string) error {
	// Read the file contents
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return err
	}

	// Parse the HCL file
	p := hclparse.NewParser()
	f, diags := p.ParseHCL(data, filePath)
	if diags.HasErrors() {
		return errors.New(diags.Error())
	}

	// Get the variables block
	variablesBlock := f.Body.(*hcl.BodyContent).Blocks[0]

	// Sort the variables alphabetically
	sort.Slice(variablesBlock.Body.Items, func(i, j int) bool {
		return variablesBlock.Body.Items[i].(hcl.Expression).Variables()[0].Name < variablesBlock.Body.Items[j].(hcl.Expression).Variables()[0].Name
	})

	// Marshal the sorted variables back to HCL
	sortedHCL, err := json.MarshalIndent(variablesBlock, "", "\t")
	if err != nil {
		return err
	}

	// Write the sorted HCL back to the file
	err = ioutil.WriteFile(filePath, []byte(sortedHCL), 0644)
	if err != nil {
		return err
	}

	return nil
}