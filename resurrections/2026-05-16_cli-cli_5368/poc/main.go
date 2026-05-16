// Proof of concept: paginated PR file listing via GitHub GraphQL API
// Uses only: github.com/cli/go-gh (real gh CLI library) + stdlib
// Run: go run main.go <PR_NUMBER>
// Requires: GH_TOKEN env var or `gh auth login` already done
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"

	"github.com/cli/go-gh/v2/pkg/api"
)

// GraphQL response structs
type pageInfo struct {
	HasNextPage bool   `json:"hasNextPage"`
	EndCursor   string `json:"endCursor"`
}

type fileNode struct {
	Path      string `json:"path"`
	Additions int    `json:"additions"`
	Deletions int    `json:"deletions"`
}

type filesConnection struct {
	PageInfo   pageInfo   `json:"pageInfo"`
	TotalCount int        `json:"totalCount"`
	Nodes      []fileNode `json:"nodes"`
}

type prFiles struct {
	Files filesConnection `json:"files"`
}

type prResponse struct {
	Repository struct {
		PullRequest prFiles `json:"pullRequest"`
	} `json:"repository"`
}

const prFilesQuery = `
query($owner: String!, $repo: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      files(first: 100, after: $cursor) {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          path
          additions
          deletions
        }
      }
    }
  }
}
`

// fetchAllFiles pages through the GraphQL files connection until exhausted.
// This removes the hard 100-file cap that the REST endpoint has.
func fetchAllFiles(client api.GQLClient, owner, repo string, prNumber int) ([]fileNode, int, error) {
	var allFiles []fileNode
	totalCount := 0
	var cursor *string

	for {
		variables := map[string]interface{}{
			"owner":  owner,
			"repo":   repo,
			"number": prNumber,
			"cursor": cursor,
		}

		var resp prResponse
		if err := client.Do(prFilesQuery, variables, &resp); err != nil {
			return nil, 0, fmt.Errorf("GraphQL query failed: %w", err)
		}

		files := resp.Repository.PullRequest.Files
		totalCount = files.TotalCount
		allFiles = append(allFiles, files.Nodes...)

		if !files.PageInfo.HasNextPage {
			break
		}
		next := files.PageInfo.EndCursor
		cursor = &next
	}

	return allFiles, totalCount, nil
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: main <pr_number>")
		os.Exit(1)
	}
	prNumber, err := strconv.Atoi(os.Args[1])
	if err != nil {
		fmt.Fprintf(os.Stderr, "invalid PR number: %v\n", err)
		os.Exit(1)
	}

	// go-gh auto-resolves owner/repo from git remote and auth from GH_TOKEN / gh keyring
	repo, err := currentRepo()
	if err != nil {
		fmt.Fprintf(os.Stderr, "could not detect repo: %v\n", err)
		os.Exit(1)
	}

	client, err := api.NewGraphQLClient(api.ClientOptions{})
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to create GraphQL client: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Fetching all files for PR #%d in %s/%s ...\n", prNumber, repo.Owner, repo.Name)

	files, total, err := fetchAllFiles(client, repo.Owner, repo.Name, prNumber)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Total files reported by API: %d | fetched: %d\n\n", total, len(files))

	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(files); err != nil {
		fmt.Fprintf(os.Stderr, "json encode error: %v\n", err)
		os.Exit(1)
	}
}

// currentRepo resolves owner+name from the git remote using go-gh.
type repoRef struct{ Owner, Name string }

func currentRepo() (repoRef, error) {
	ghr, err := api.CurrentRepository()
	if err != nil {
		return repoRef{}, err
	}
	return repoRef{Owner: ghr.Owner(), Name: ghr.Name()}, nil
}
