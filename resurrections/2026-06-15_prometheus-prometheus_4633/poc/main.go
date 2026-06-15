package main

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/golang/snappy"
	"github.com/grpc-ecosystem/grpc-gateway/v2/protoc_gen_openapiv2/options"
	"github.com/prometheus/client_golang/api"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"golang.org/x/net/context"
	"golang.org/x/sync/errgroup"
)

func main() {
	// Set up logging
	log.SetFlags(log.LstdFlags | log.LUTC)
	log.SetPrefix("prometheus-k8s-proxy: ")

	// Set up flags
	var (
		k8sAPIURL    = flag.String("k8s-api-url", "https://kubernetes.default.svc.cluster.local", "Kubernetes API URL")
		k8sCertFile  = flag.String("k8s-cert-file", "", "Path to Kubernetes client certificate file")
		k8sKeyFile   = flag.String("k8s-key-file", "", "Path to Kubernetes client key file")
		prometheusURL = flag.String("prometheus-url", "http://localhost:9090", "Prometheus URL")
		proxyPort    = flag.Int("proxy-port", 8080, "Proxy port")
	)
	flag.Parse()

	// Load Kubernetes client certificate and key
	var tlsConfig *tls.Config
	if *k8sCertFile != "" && *k8sKeyFile != "" {
		cert, err := ioutil.ReadFile(*k8sCertFile)
		if err != nil {
			log.Fatalf("Failed to read Kubernetes client certificate file: %v", err)
		}
		key, err := ioutil.ReadFile(*k8sKeyFile)
		if err != nil {
			log.Fatalf("Failed to read Kubernetes client key file: %v", err)
		}
		 tlsConfig = &tls.Config{
			Certificates: []tls.Certificate{
				{
					Certificate: [][]byte{cert},
					PrivateKey:  key,
				},
			},
		}
	}

	// Create a new Prometheus client
	prometheusClient, err := api.NewClient(api.Config{
		Address: *prometheusURL,
	})
	if err != nil {
		log.Fatalf("Failed to create Prometheus client: %v", err)
	}

	// Create a new Kubernetes API client
	k8sClient, err := getK8sClient(*k8sAPIURL, tlsConfig)
	if err != nil {
		log.Fatalf("Failed to create Kubernetes API client: %v", err)
	}

	// Start the proxy server
	proxyServer := &http.Server{
		Addr: fmt.Sprintf(":%d", *proxyPort),
	}
	proxyServer.Handler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Handle Prometheus scrape requests
		if strings.HasPrefix(r.URL.Path, "/metrics") {
			err = handlePrometheusScrape(k8sClient, w, r)
		} else {
			err = fmt.Errorf("unsupported URL path: %s", r.URL.Path)
		}
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	})

	log.Printf("Proxy server listening on port %d", *proxyPort)
	if err := proxyServer.ListenAndServeTLS("", ""); err != nil {
		log.Fatalf("Failed to start proxy server: %v", err)
	}
}

func getK8sClient(apiURL string, tlsConfig *tls.Config) (*http.Client, error) {
	transport := &http.Transport{
		TLSClientConfig: tlsConfig,
	}
	return &http.Client{Transport: transport}, nil
}

func handlePrometheusScrape(k8sClient *http.Client, w http.ResponseWriter, r *http.Request) error {
	// Implement Prometheus scrape logic here
	// For demonstration purposes, return a simple metric
	metric := prometheus.MustNewConstMetric(
		prometheus.NewDesc("", "", nil),
		prometheus.GaugeValue,
		1,
	)
	err := metric.Write(w)
	if err != nil {
		return err
	}
	return nil
}