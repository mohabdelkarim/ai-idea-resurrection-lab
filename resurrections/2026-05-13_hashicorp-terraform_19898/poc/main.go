package main

import (
	"encoding/json"
	"errors"
	"fmt"
)

type ObjectType struct {
	Properties map[string]Property `json:"properties"`
}

type Property struct {
	Type     string `json:"type"`
	Optional bool   `json:"optional,omitempty"`
}

func NewObjectType(properties map[string]Property) *ObjectType {
	return &ObjectType{Properties: properties}
}

func (o *ObjectType) Validate(instance map[string]interface{}) error {
	for key, value := range instance {
		property, ok := o.Properties[key]
		if !ok {
			return fmt.Errorf("unknown property: %s", key)
		}
		if value == nil && property.Optional {
			continue
		}
		if value == nil && !property.Optional {
			return fmt.Errorf("property %s is required", key)
		}
		if err := validateType(value, property.Type); err != nil {
			return err
		}
		}
		for key := range o.Properties {
			if _, ok := instance[key]; !ok && !o.Properties[key].Optional {
				return fmt.Errorf("property %s is required", key)
			}
		}
		return nil
}

func validateType(value interface{}, typ string) error {
	switch typ {
	case "string":
		if _, ok := value.(string); !ok {
			return errors.New("expected string")
		}
	case "list":
		if _, ok := value.([]interface{}); !ok {
			return errors.New("expected list")
		}
	default:
		return fmt.Errorf("unsupported type: %s", typ)
	}
	return nil
}

func main() {
	objectType := NewObjectType(map[string]Property{
		"bypass": {
			Type:     "list",
			Optional: true,
		},
		"ip_rules": {
			Type:     "list",
			Optional: true,
		},
		"virtual_network_subnet_ids": {
			Type:     "list",
			Optional: true,
		},
		"required_property": {
			Type:     "string",
			Optional: false,
		},
	})
	instance := map[string]interface{}{
		"bypass":                     []interface{}{"a", "b"},
		"ip_rules":                   []interface{}{"c", "d"},
		"virtual_network_subnet_ids": []interface{}{"e", "f"},
		"required_property":          "required",
	}
	err := objectType.Validate(instance)
	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println("Instance is valid")
	}
	jsonInstance, _ := json.Marshal(instance)
	fmt.Println(string(jsonInstance))
}