package main

import (
	"context"
	"fmt"
	"log"

	"k8s.io/api/apps/v1"
	"k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/informers"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
)

func main() {
	// Create a new Kubernetes client
	config, err := rest.InClusterConfig()
	if err != nil {
		log.Fatalf("Error creating client config: %v", err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		log.Fatalf("Error creating clientset: %v", err)
	}

	// Create an informer to watch for node creation events
	nodeInformerFactory := informers.NewSharedInformerFactory(clientset, 0)
	nodeInformer := nodeInformerFactory.Core().V1().Nodes()

	nodeInformer.Lister().AddEventHandler(
		informers.ResourceEventHandlerFuncs{
			AddFunc: func(obj interface{}) {
				node, ok := obj.(*v1.Node)
				if !ok {
					log.Println("Failed to type assert node")
					return
				}

				// Create a new job on each node
				createJob(clientset, node)
			},
		},
	)

	nodeInformerFactory.Start(context.Background().Done())

	select {}
}

func createJob(clientset *kubernetes.Clientset, node *v1.Node) {
	// Create a new job
	job := &batchv1.Job{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "setup-node",
			Namespace: "default",
		},
		Spec: batchv1.JobSpec{
			Template: v1.PodTemplateSpec{
				Spec: v1.PodSpec{
					Containers: []v1.Container{
						{
							Name:  "setup-node",
							Image: "busybox",
							Command: []string{
								"sh",
								"-c",
								"echo 'Node setup complete'",
						},
					},
					RestartPolicy: v1.RestartPolicyNever,
				},
			},
		},
	}

	// Add a unique annotation to the job
	job.Annotations = map[string]string{
		"setup-node": "true",
	}

	_, err := clientset.BatchV1().Jobs("default").Create(context.Background(), job, metav1.CreateOptions{})
	if err != nil {
		log.Printf("Error creating job: %v", err)
	}

	log.Println("Job created on node", node.Name)
}