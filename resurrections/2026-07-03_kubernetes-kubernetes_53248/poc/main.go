package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/informers"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/cache"
)

func main() {
	if len(os.Args) != 3 {
		fmt.Printf("Usage: %s <service-account-name> <namespace>\n", os.Args[0])
		os.Exit(1)
	}

	saName := os.Args[1]
	namespace := os.Args[2]

	config, err := rest.InClusterConfig()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	rbInformerFactory := informers.NewSharedInformerFactory(clientset, 0)
	rbLister := rbInformerFactory.Rbac().V1().RoleBindings().Lister()
	crbLister := rbInformerFactory.Rbac().V1().ClusterRoleBindings().Lister()

	rbInformerFactory.Start(context.Background().Done())

	err = rbInformerFactory.WaitForCacheSync(context.Background().Done())
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	rbs, err := rbLister.List(context.Background(), func(rb *rbacv1.RoleBinding) bool {
		return rb.Spec.ServiceAccount.Name == saName && rb.Spec.ServiceAccount.Namespace == namespace
	})
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	crbs, err := crbLister.List(context.Background(), func(crb *rbacv1.ClusterRoleBinding) bool {
		return crb.Spec.ServiceAccount.Name == saName && crb.Spec.ServiceAccount.Namespace == namespace
	})
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	if len(rbs) > 0 {
		fmt.Printf("RoleBindings:\n")
		for _, rb := range rbs {
			fmt.Printf("  - %s/%s\n", rb.Namespace, rb.Name)
		}
	}

	if len(crbs) > 0 {
		fmt.Printf("ClusterRoleBindings:\n")
		for _, crb := range crbs {
			fmt.Printf("  - %s\n", crb.Name)
		}
	}

	if len(rbs) == 0 && len(crbs) == 0 {
		fmt.Printf("No RoleBindings or ClusterRoleBindings found for ServiceAccount %s/%s\n", namespace, saName)
	}
}