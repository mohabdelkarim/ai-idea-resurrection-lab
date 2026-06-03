package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"log"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/service/athena"
)

type athenaDataSource struct {
	cfg     *config.Config
	athena  *athena.Client
	region  string
}

func newAthenaDataSource(region string) (*athenaDataSource, error) {
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		return nil, err
	}

	athenaClient := athena.NewFromConfig(cfg)

	return &athenaDataSource{
		cfg:    &cfg,
		athena: athenaClient,
		region: region,
	}, nil

}

func (a *athenaDataSource) executeQuery(query string) (*sql.Rows, error) {
	params := &athena.StartQueryExecutionInput{
		QueryString:    aws.String(query),
		QueryExecutionContext: &athena.QueryExecutionContext{
			Database: aws.String("default"),
		},
	}

	response, err := a.athena.StartQueryExecution(context.TODO(), params)
	if err != nil {
		return nil, err
	}

	queryExecutionId := response.QueryExecutionId

	for {
		status, err := a.getQueryStatus(queryExecutionId)
		if err != nil {
			return nil, err
		}

		switch status.Status.State {
		case "SUCCEEDED":
			results, err := a.getQueryResults(queryExecutionId)
			if err != nil {
				return nil, err
			}
			return results, nil
		case "FAILED":
			return nil, errors.New("query failed")
		default:
			log.Println("query is still running...")
		}

		// wait a bit before checking again
		// NOTE: in a real implementation you'd want to use a more robust waiting mechanism
		log.Println("sleeping...")
	}
}

func (a *athenaDataSource) getQueryStatus(queryExecutionId *string) (*athena.QueryExecution, error) {
	params := &athena.GetQueryExecutionInput{
		QueryExecutionId: queryExecutionId,
	}

	response, err := a.athena.GetQueryExecution(context.TODO(), params)
	if err != nil {
		return nil, err
	}

	return response.QueryExecution, nil
}

func (a *athenaDataSource) getQueryResults(queryExecutionId *string) (*sql.Rows, error) {
	params := &athena.GetQueryResultsInput{
		QueryExecutionId: queryExecutionId,
	}

	response, err := a.athena.GetQueryResults(context.TODO(), params)
	if err != nil {
		return nil, err
	}

	// convert to sql.Rows
	// NOTE: this is a very simplified example; a real implementation would need to handle types, etc.
	rows := [][]string{}
	for _, result := range response.ResultSet.Rows {
		row := []string{}
		for _, datum := range result.Data {
			row = append(row, *datum.VarCharValue)
		}
		rows = append(rows, row)
	}

	return sql.NewRows([]string{"result"}, rows), nil
}

func main() {
	awsRegion := "us-west-2"
	a, err := newAthenaDataSource(awsRegion)
	if err != nil {
		log.Fatal(err)
	}

	query := "SELECT * FROM my_table"
	results, err := a.executeQuery(query)
	if err != nil {
		log.Fatal(err)
	}
	defer results.Close()

	for results.Next() {
		var result string
		err = results.Scan(&result)
		if err != nil {
			log.Fatal(err)
		}
		log.Println(result)
	}
}