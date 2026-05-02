# Terraform Init Command
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/hashicorp/terraform-cdk-go/cdktf"
)

func main() {
	// Load AWS configuration
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatal(err)
	}

	// Create S3 client
	s3Client := s3.NewFromConfig(cfg)

	// Create DynamoDB client
	dynamoDBClient := dynamodb.NewFromConfig(cfg)

	// Get S3 bucket and lock table names from Terraform configuration
	bucketName := "my-bucket"
	lockTableName := "my-lock-table"

	// Check if S3 bucket exists
	bucketExists, err := s3Client.HeadBucket(context.TODO(), &s3.HeadBucketInput{
		Bucket: aws.String(bucketName),
	})
	if err != nil {
		if err.(type) == s3.NotFoundException {
			// Create S3 bucket with versioning enabled
			_, err := s3Client.CreateBucket(context.TODO(), &s3.CreateBucketInput{
				Bucket: aws.String(bucketName),
			})
			if err != nil {
				log.Fatal(err)
			}

			// Enable versioning on S3 bucket
			_, err := s3Client.PutBucketVersioning(context.TODO(), &s3.PutBucketVersioningInput{
				Bucket: aws.String(bucketName),
				VersioningConfiguration: &s3.VersioningConfiguration{
					Status: aws.String("Enabled"),
				},
			})
			if err != nil {
				log.Fatal(err)
			}
		} else {
			log.Fatal(err)
		}
	}

	// Check if lock table exists
	lockTableExists, err := dynamoDBClient.DescribeTable(context.TODO(), &dynamodb.DescribeTableInput{
		TableName: aws.String(lockTableName),
	})
	if err != nil {
		if err.(type) == dynamodb.ResourceNotFoundException {
			// Create lock table
			_, err := dynamoDBClient.CreateTable(context.TODO(), &dynamodb.CreateTableInput{
				TableName: aws.String(lockTableName),
				AttributeDefinitions: []dynamodb.AttributeDefinition{
					{
						AttributeName: aws.String("LockID"),
						AttributeType:  aws.String("S"),
					},
				},
				KeySchema: []dynamodb.KeySchemaElement{
					{
						AttributeName: aws.String("LockID"),
						KeyType:       aws.String("HASH"),
					},
				},
				TableStatus: aws.String("ACTIVE"),
			})
			if err != nil {
				log.Fatal(err)
			}
		} else {
			log.Fatal(err)
		}
	}

	fmt.Println("S3 bucket and lock table created successfully")

	// Test the S3 bucket and lock table
	_, err = s3Client.ListBuckets(context.TODO(), &s3.ListBucketsInput{})
	if err != nil {
		log.Fatal(err)
	}

	_, err = dynamoDBClient.ListTables(context.TODO(), &dynamodb.ListTablesInput{})
	if err != nil {
		log.Fatal(err)
	}
}