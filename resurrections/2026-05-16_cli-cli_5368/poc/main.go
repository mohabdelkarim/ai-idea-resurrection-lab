package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/cli/go-gh"
	"github.com/cli/go-gh/auth"
	"github.com/cli/go-gh/transport"
	"github.com/shurcooL/github_flate"
)

type File struct {
	Filename string `json:"filename"`
}

type PullRequest struct {
	Files []File `json:"files"`
}

func main() {
	// Authentication
	token, err := auth.GetToken("github.com")
	if err != nil {
		fmt.Println(err)
		return
	}
	rateLimit := &transport.RateLimit{
		Token: token,
	}
	tp := transport.NewChain(rateLimit, transport.Default)
	client, err := gh.NewClient(tp)
	if err != nil {
		fmt.Println(err)
		return
	}

	// Fetch files
	var files []File
	err = fetchFiles(client, 12345, &files)
	if err != nil {
		fmt.Println(err)
		return
	}

	// Output
	data, err := json.MarshalIndent(files, "", "\t")
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(string(data))
}

func fetchFiles(client *gh.Client, prNumber int, accumulator *[]File) error {
	var query struct {
		Repository struct {
			PullRequest struct {
				Files struct {
					Edges []struct {
						Node File `json:"node"`
					} `json:"edges"`
					PageInfo github_flate.PageInfo `json:"pageInfo"`
				} `json:"files"`
			} `json:"pullRequest"`
		} `json:"repository"`
	}
	vars := map[string]interface{}{
		"prNumber": prNumber,
		"repoOwner": "your_username",
		"repoName":   "your_repo",
	}
	for {
		err := client.GraphQL().Query(&query, vars)
		if err != nil {
			return err
		}
		for _, edge := range query.Repository.PullRequest.Files.Edges {
			*accumulator = append(*accumulator, edge.Node)
		}
		if !query.Repository.PullRequest.Files.PageInfo.HasNextPage {
			break
		}
		vars["cursor"] = query.Repository.PullRequest.Files.PageInfo.EndCursor
	}
	return nil
}