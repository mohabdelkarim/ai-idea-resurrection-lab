package main

import (
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"sync"

	"github.com/golang/snappy"
)

const (
	walSegmentFileName = "wal_segment"
	walSegmentFileExt  = ".snappy"
)

type walSegment struct {
	filePath string
	data     []byte
}

func loadWalSegment(filePath string) (*walSegment, error) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}
	decompressedData, err := snappy.Decode(nil, data)
	if err != nil {
		return nil, err
	}
	return &walSegment{filePath: filePath, data: decompressedData}, nil
}

func loadWalSegmentsInParallel(filePaths []string, numWorkers int) ([]*walSegment, error) {
	var wg sync.WaitGroup
	var mu sync.Mutex
	segments := make([]*walSegment, 0, len(filePaths))
	errChan := make(chan error, numWorkers)
	segmentChan := make(chan *walSegment, numWorkers)

	for i := 0; i < numWorkers; i++ {
		go func() {
			for filePath := range segmentChan {
				segment, err := loadWalSegment(filePath)
				if err != nil {
					errChan <- err
					return
				}
				mu.Lock()
				segments = append(segments, segment)
				mu.Unlock()
			}
		}()
	}

	for _, filePath := range filePaths {
		segmentChan <- filePath
	}
	close(segmentChan)

	for i := 0; i < numWorkers; i++ {
		if err := <-errChan; err != nil {
			return nil, err
		}
	}

	return segments, nil
}

func main() {
	// Create a temporary directory to store WAL segments.
	tempDir, err := ioutil.TempDir("", "wal_segments")
	if err != nil {
		log.Fatal(err)
	}
	defer os.RemoveAll(tempDir)

	// Create some sample WAL segments.
	for i := 0; i < 10; i++ {
		filePath := filepath.Join(tempDir, fmt.Sprintf(walSegmentFileName+"_%d"+walSegmentFileExt, i))
		data := []byte(fmt.Sprintf("Sample WAL segment data %d", i))
		compressedData, err := snappy.Encode(nil, data)
		if err != nil {
			log.Fatal(err)
		}
		err = ioutil.WriteFile(filePath, compressedData, 0666)
		if err != nil {
			log.Fatal(err)
		}
	}

	// Load WAL segments in parallel.
	filePaths, err := filepath.Glob(filepath.Join(tempDir, walSegmentFileName+"*"+walSegmentFileExt))
	if err != nil {
		log.Fatal(err)
	}
	segments, err := loadWalSegmentsInParallel(filePaths, 5)
	if err != nil {
		log.Fatal(err)
	}

	// Print loaded WAL segments.
	for _, segment := range segments {
		fmt.Println(segment.filePath)
	}
}