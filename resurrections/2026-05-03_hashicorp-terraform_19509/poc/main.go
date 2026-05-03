# proof_of_concept_code
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	"github.com/hashicorp/terraform-plugin-sdk/v2/plugin"
)

func main() {
	plugin.Serve(&plugin.ServeOpts{
		ProviderFunc: func() *schema.Provider {
			return &schema.Provider{
				Schema: map[string]*schema.Schema{
					"command": {
						Type:     schema.TypeString,
						Required: true,
					},
					"output": {
						Type:     schema.TypeString,
						Computed: true,
					},
				},
				ResourcesMap: map[string]*schema.Resource{
					"example": resourceExample(),
				},
			}
		},
	})
}

func resourceExample() *schema.Resource {
	return &schema.Resource{
		Schema: map[string]*schema.Schema{
			"command": {
				Type:     schema.TypeString,
				Required: true,
			},
			"output": {
				Type:     schema.TypeString,
				Computed: true,
			},
		},
		Create: resourceExampleCreate,
		Read:   resourceExampleRead,
	}
}

func resourceExampleCreate(d *schema.ResourceData, meta interface{}) error {
	cmd := exec.Command("sh", "-c", d.Get("command").(string))
	output, err := cmd.CombinedOutput()
	if err != nil {
		return err
	}
	d.Set("output", string(output))
	d.SetId("example-id")
	return nil
}

func resourceExampleRead(d *schema.ResourceData, meta interface{}) error {
	return nil
}

func resourceExampleDelete(d *schema.ResourceData, meta interface{}) error {
	return nil
}
