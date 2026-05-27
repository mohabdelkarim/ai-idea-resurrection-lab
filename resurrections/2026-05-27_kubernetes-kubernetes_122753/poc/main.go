package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"golang.org/x/sys"
	"k8s.io/api/apps/v1"
	"k8s.io/client-go/informers"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
)

func main() {
	// Create a new Kubernetes client
	config, err := rest.InClusterConfig()
	if err != nil {
		log.Fatal(err)
	}
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		log.Fatal(err)
	}

	// Create an informer factory
	informerFactory := informers.NewSharedInformerFactory(clientset, 0)

	// Create a new DaemonSet controller
	controller := NewDaemonSetController(clientset, informerFactory)

	// Run the controller
	if err := controller.Run(context.Background()); err != nil {
		log.Fatal(err)
	}
}

type DaemonSetController struct {
	clientset    *kubernetes.Clientset
	informerFactory informers.SharedInformerFactory
}

func NewDaemonSetController(clientset *kubernetes.Clientset, informerFactory informers.SharedInformerFactory) *DaemonSetController {
	return &DaemonSetController{
		clientset:    clientset,
		informerFactory: informerFactory,
	}
}

func (c *DaemonSetController) Run(ctx context.Context) error {
	// Start the informer factory
	c.informerFactory.Start(ctx.Done())

	// Get the DaemonSet informer
	daemonSetInformer := c.informerFactory.Apps().V1().DaemonSets()

	// Handle add, update, and delete events
	daemonSetInformer.Informer().AddEventHandler(
	informers.ResourceEventHandlerFuncs{
		AddFunc: func(obj interface{}) {
			c.handleDaemonSetAdd(obj)
		},
		UpdateFunc: func(oldObj, newObj interface{}) {
			c.handleDaemonSetUpdate(oldObj, newObj)
		},
		DeleteFunc: func(obj interface{}) {
			c.handleDaemonSetDelete(obj)
		},
	})

	// Run the informer factory until the context is cancelled
	for {
		sel, err := c.informerFactory.WaitForCacheSync(ctx.Done())
	if err != nil {
		return err
	}
	if !sel {
		return fmt.Errorf("failed to sync cache")
	}
	}
}

func (c *DaemonSetController) handleDaemonSetAdd(obj interface{}) {
	daemonSet, ok := obj.(*v1.DaemonSet)
	if !ok {
		log.Printf("unexpected type: %T", obj)
		return
	}

	// Get the node's capacity
	nodeList, err := c.clientset.CoreV1().Nodes().List(context.Background(), &v1.ListOptions{})
	if err != nil {
		log.Printf("failed to list nodes: %v", err)
		return
	}

	nodeCapacities := make(map[string]v1.ResourceList)
	for _, node := range nodeList.Items {
		nodeCapacities[node.Name] = node.Status.Capacity
	}

	// Update the DaemonSet's resources based on the node's capacity
	for _, node := range nodeList.Items {
		resources, ok := nodeCapacities[node.Name]
	if !ok {
		continue
	}

		// Calculate the resources needed for the DaemonSet
		// For simplicity, let's assume we need 100m CPU and 128Mi memory per node
		resources = v1.ResourceList{
		"cpu":    *resource.NewMilliQuantity(100, resource.DecimalSI),
		"memory": *resource.NewQuantity(128*1024*1024, resource.BinarySI),
	}

		// Update the DaemonSet's resources
		daemonSet.Spec.Template.Spec.Containers[0].Resources = v1.ResourceRequirements{
		Requests: resources,
		Limits:   resources,
	}

		// Update the DaemonSet
		_, err = c.clientset.AppsV1().DaemonSets(daemonSet.Namespace).Update(context.Background(), daemonSet, metav1.UpdateOptions{})
		if err != nil {
			log.Printf("failed to update DaemonSet: %v", err)
		}
	}
}

func (c *DaemonSetController) handleDaemonSetUpdate(oldObj, newObj interface{}) {
	// No-op
}

func (c *DaemonSetController) handleDaemonSetDelete(obj interface{}) {
	// No-op
}