package main

import (
	"fmt"
	"math"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// MemoryEstimator estimates memory requirements for Prometheus
type MemoryEstimator struct {
	metricsCount int
	scrapeInterval float64
	storageRetention float64
}

// NewMemoryEstimator returns a new MemoryEstimator
func NewMemoryEstimator(metricsCount int, scrapeInterval, storageRetention float64) *MemoryEstimator {
	return &MemoryEstimator{
		metricsCount:     metricsCount,
		scrapeInterval:   scrapeInterval,
		storageRetention: storageRetention,
	}
}

// EstimateMemory estimates memory requirements in bytes
func (e *MemoryEstimator) EstimateMemory() (float64, error) {
	if e.metricsCount <= 0 {
		return 0, fmt.Errorf("metrics count must be greater than 0")
	}
	if e.scrapeInterval <= 0 {
		return 0, fmt.Errorf("scrape interval must be greater than 0")
	}
	if e.storageRetention <= 0 {
		return 0, fmt.Errorf("storage retention must be greater than 0")
	}

	// Simple estimation formula: metricsCount * scrapeInterval * storageRetention * 1024 * 1024 * 10
	// This formula is fictional and used only for demonstration purposes
	estimatedMemory := float64(e.metricsCount) * e.scrapeInterval * e.storageRetention * 1024 * 1024 * 10

	return estimatedMemory, nil
}

func main() {
	// Create a new MemoryEstimator
	estimator := NewMemoryEstimator(10000, 15, 24)

	estimatedMemory, err := estimator.EstimateMemory()
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Printf("Estimated memory requirements: %.2f MB\n", estimatedMemory/1024/1024)

	// Register Prometheus metrics
	prometheus.MustRegister(newMetricsCountGauge(estimator.metricsCount))
	prometheus.MustRegister(newScrapeIntervalGauge(estimator.scrapeInterval))
	prometheus.MustRegister(newStorageRetentionGauge(estimator.storageRetention))

	// Serve Prometheus metrics
	promhttp.Handler().ServeHTTP(nil, nil)
}

type metricsCountGauge struct {
	metricsCount int
}

func newMetricsCountGauge(metricsCount int) *metricsCountGauge {
	return &metricsCountGauge{metricsCount: metricsCount}
}

func (g *metricsCountGauge) Describe(ch chan<- *prometheus.Desc) {
	ch <- prometheus.NewDesc("memory_planning_metrics_count", "Number of metrics", nil, nil)
}

func (g *metricsCountGauge) Collect(ch chan<- prometheus.Metric) {
	ch <- prometheus.MustNewConstMetric(prometheus.NewDesc("memory_planning_metrics_count", "Number of metrics", nil, nil), prometheus.GaugeValue, float64(g.metricsCount), nil)
}

type scrapeIntervalGauge struct {
	scrapeInterval float64
}

func newScrapeIntervalGauge(scrapeInterval float64) *scrapeIntervalGauge {
	return &scrapeIntervalGauge{scrapeInterval: scrapeInterval}
}

func (g *scrapeIntervalGauge) Describe(ch chan<- *prometheus.Desc) {
	ch <- prometheus.NewDesc("memory_planning_scrape_interval", "Scrape interval", nil, nil)
}

func (g *scrapeIntervalGauge) Collect(ch chan<- prometheus.Metric) {
	ch <- prometheus.MustNewConstMetric(prometheus.NewDesc("memory_planning_scrape_interval", "Scrape interval", nil, nil), prometheus.GaugeValue, g.scrapeInterval, nil)
}

type storageRetentionGauge struct {
	storageRetention float64
}

func newStorageRetentionGauge(storageRetention float64) *storageRetentionGauge {
	return &storageRetentionGauge{storageRetention: storageRetention}
}

func (g *storageRetentionGauge) Describe(ch chan<- *prometheus.Desc) {
	ch <- prometheus.NewDesc("memory_planning_storage_retention", "Storage retention", nil, nil)
}

func (g *storageRetentionGauge) Collect(ch chan<- prometheus.Metric) {
	ch <- prometheus.MustNewConstMetric(prometheus.NewDesc("memory_planning_storage_retention", "Storage retention", nil, nil), prometheus.GaugeValue, g.storageRetention, nil)
}