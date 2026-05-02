# File: main.tf
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-abc123"
  instance_type = "t2.micro"
  tags = {
    Name        = "example"
    VERSION     = "1.0"
    Environment = "dev"
  }
}

resource "aws_resource_tag_ignore" "example" {
  resource_id = aws_instance.example.id
  ignore_tag_changes = ["VERSION"]
}

# File: aws_resource_tag_ignore.go
package main

import (
	"context"
	"fmt"

	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/validation"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/ec2"
)

func resourceAwsResourceTagIgnore() *schema.Resource {
	return &schema.Resource{
		Schema: map[string]*schema.Schema{
			"resource_id": {
				Type:     schema.TypeString,
				Required: true,
			},
			"ignore_tag_changes": {
				Type:     schema.TypeList,
				Elem: &schema.Schema{
					Type: schema.TypeString,
				},
				Required: true,
			},
		},
		Create: resourceAwsResourceTagIgnoreCreate,
		Read:   resourceAwsResourceTagIgnoreRead,
		Update: resourceAwsResourceTagIgnoreUpdate,
		Delete: resourceAwsResourceTagIgnoreDelete,
	}
}

func resourceAwsResourceTagIgnoreCreate(d *schema.ResourceData, meta interface{}) error {
	// Create the AWS session
	sess, err := session.NewSession(&aws.Config{Region: aws.String("us-west-2")}, nil)
	if err != nil {
		return err
	}

	// Get the EC2 client
	ec2Client := ec2.New(sess)

	// Get the resource ID and ignore tag changes
	resourceId := d.Get("resource_id").(string)
	ignoreTagChanges := d.Get("ignore_tag_changes").([]interface{})

	// Filter the resource tags
	tags, err := ec2Client.DescribeTags(&ec2.DescribeTagsInput{
		Filters: []*ec2.Filter{
			{
				Name: aws.String("resource-id"),
				Values: []*string{
					aws.String(resourceId),
				},
			},
		},
	})
	if err != nil {
		return err
	}

	// Ignore the specified tags
	ignoredTags := make(map[string]string)
	for _, tag := range ignoreTagChanges {
		ignoredTags[*tag.(string)] = ""
	}

	// Update the resource tags
	_, err = ec2Client.CreateTags(&ec2.CreateTagsInput{
		Resources: []*string{
			aws.String(resourceId),
		},
		Tags: []*ec2.Tag{
			{
				Key:   aws.String("Name"),
				Value: aws.String("example"),
			},
			{
				Key:   aws.String("Environment"),
				Value: aws.String("dev"),
			},
		},
	})
	if err != nil {
		return err
	}

	// Set the resource ID
	d.SetId(resourceId)

	return nil
}

func resourceAwsResourceTagIgnoreRead(d *schema.ResourceData, meta interface{}) error {
	// Read the resource tags
	sess, err := session.NewSession(&aws.Config{Region: aws.String("us-west-2")}, nil)
	if err != nil {
		return err
	}

	// Get the EC2 client
	ec2Client := ec2.New(sess)

	// Get the resource ID
	resourceId := d.Id()

	// Filter the resource tags
	tags, err := ec2Client.DescribeTags(&ec2.DescribeTagsInput{
		Filters: []*ec2.Filter{
			{
				Name: aws.String("resource-id"),
				Values: []*string{
					aws.String(resourceId),
				},
			},
		},
	})
	if err != nil {
		return err
	}

	// Update the resource data
	d.Set("resource_id", resourceId)
	return nil
}

func resourceAwsResourceTagIgnoreUpdate(d *schema.ResourceData, meta interface{}) error {
	// Update the resource tags
	sess, err := session.NewSession(&aws.Config{Region: aws.String("us-west-2")}, nil)
	if err != nil {
		return err
	}

	// Get the EC2 client
	ec2Client := ec2.New(sess)

	// Get the resource ID and ignore tag changes
	resourceId := d.Get("resource_id").(string)
	ignoreTagChanges := d.Get("ignore_tag_changes").([]interface{})

	// Filter the resource tags
	tags, err := ec2Client.DescribeTags(&ec2.DescribeTagsInput{
		Filters: []*ec2.Filter{
			{
				Name: aws.String("resource-id"),
				Values: []*string{
					aws.String(resourceId),
				},
			},
		},
	})
	if err != nil {
		return err
	}

	// Ignore the specified tags
	ignoredTags := make(map[string]string)
	for _, tag := range ignoreTagChanges {
		ignoredTags[*tag.(string)] = ""
	}

	// Update the resource tags
	_, err = ec2Client.CreateTags(&ec2.CreateTagsInput{
		Resources: []*string{
			aws.String(resourceId),
		},
		Tags: []*ec2.Tag{
			{
				Key:   aws.String("Name"),
				Value: aws.String("example"),
			},
			{
				Key:   aws.String("Environment"),
				Value: aws.String("dev"),
			},
		},
	})
	if err != nil {
		return err
	}

	return nil
}

func resourceAwsResourceTagIgnoreDelete(d *schema.ResourceData, meta interface{}) error {
	// Delete the resource tags
	sess, err := session.NewSession(&aws.Config{Region: aws.String("us-west-2")}, nil)
	if err != nil {
		return err
	}

	// Get the EC2 client
	ec2Client := ec2.New(sess)

	// Get the resource ID
	resourceId := d.Id()

	// Filter the resource tags
	tags, err := ec2Client.DescribeTags(&ec2.DescribeTagsInput{
		Filters: []*ec2.Filter{
			{
				Name: aws.String("resource-id"),
				Values: []*string{
					aws.String(resourceId),
				},
			},
		},
	})
	if err != nil {
		return err
	}

	// Delete the resource tags
	_, err = ec2Client.DeleteTags(&ec2.DeleteTagsInput{
		Resources: []*string{
			aws.String(resourceId),
		},
	})
	if err != nil {
		return err
	}

	return nil
}