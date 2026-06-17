package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatal("Usage: go get <url>")
	}
	url := os.Args[1]
	res, err := http.Get(url)
	if err != nil {
		log.Fatalf("Failed to get %s: %v", url, err)
	}
	defer res.Body.Close()

	totalSize := res.ContentLength
	if totalSize == -1 {
		totalSize = 0
	}
	downloaded := 0
	start := time.Now()
	lastUpdate := time.Now()
	lastDownloaded := 0

	buf := make([]byte, 1024*1024)
	for {
		n, err := res.Body.Read(buf)
	if err != nil && err != io.EOF {
		log.Fatalf("Failed to read response body: %v", err)
	}
	if n == 0 {
		break
	}
	downloaded += n

	if time.Since(lastUpdate) > 500*time.Millisecond {
		lastUpdate = time.Now()
		speed := float64(downloaded-lastDownloaded) / time.Since(lastUpdate).Seconds()
		lastDownloaded = downloaded

		pct := 0.0
		if totalSize > 0 {
			pct = (float64(downloaded) / float64(totalSize)) * 100
		}

		fmt.Printf("\rDownloading... %.2f%% (%.2f MB/s)", pct, speed/1024/1024)
	}
}
	fmt.Println()
	elapsed := time.Since(start)
	fmt.Printf("Downloaded %d bytes in %s\n", downloaded, elapsed)
}