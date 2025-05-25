# Getting Started with Istio

This guide provides a step-by-step walkthrough for installing Istio, deploying a sample application, and exploring Istio's core features.

## Prerequisites

Before you begin, ensure you have:

- A Kubernetes cluster (version 1.19 or later)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed and configured
- Cluster administrator permissions

## Installation Process

### Step 1: Download Istio

Download and extract the latest Istio release:

```bash
curl -L https://istio.io/downloadIstio | sh -
```

Navigate to the Istio package directory (replace with your version):

```bash
cd istio-1.26.0
```

Add the `istioctl` client to your path:

```bash
export PATH=$PWD/bin:$PATH
```

### Step 2: Install Istio

Install Istio using the demo profile without gateways:

```bash
istioctl install -f samples/bookinfo/demo-profile-no-gateways.yaml -y
```

The demo profile is suitable for testing but not for production environments. For production, consider other profiles or custom configurations.

### Step 3: Enable Automatic Sidecar Injection

Label the default namespace to enable automatic Envoy sidecar injection:

```bash
kubectl label namespace default istio-injection=enabled
```

### Step 4: Install Kubernetes Gateway API CRDs

The Kubernetes Gateway API CRDs are required for Istio's gateway functionality:

```bash
kubectl get crd gateways.gateway.networking.k8s.io &> /dev/null || \
{ kubectl kustomize "github.com/kubernetes-sigs/gateway-api/config/crd?ref=v1.3.0-rc.1" | kubectl apply -f -; }
```

## Deploy the Sample Application

### Step 1: Deploy the Bookinfo Application

Deploy the Bookinfo sample application:

```bash
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
```

Verify the services are running:

```bash
kubectl get services
```

Verify the pods are running with sidecars (should show 2/2 READY):

```bash
kubectl get pods
```

### Step 2: Validate the Application

Confirm the application is running inside the cluster:

```bash
kubectl exec "$(kubectl get pod -l app=ratings -o jsonpath='{.items[0].metadata.name}')" -c ratings -- curl -sS productpage:9080/productpage | grep -o "<title>.*</title>"
```

You should see: `<title>Simple Bookstore App</title>`

## Expose the Application

### Step 1: Create a Gateway

Create a Kubernetes Gateway for the Bookinfo application:

```bash
kubectl apply -f samples/bookinfo/gateway-api/bookinfo-gateway.yaml
```

### Step 2: Configure the Gateway Service Type

Change the service type to ClusterIP:

```bash
kubectl annotate gateway bookinfo-gateway networking.istio.io/service-type=ClusterIP --namespace=default
```

Verify the gateway status:

```bash
kubectl get gateway
```

### Step 3: Access the Application

Use port forwarding to access the application:

```bash
kubectl port-forward svc/bookinfo-gateway-istio 8080:80
```

Open your browser and navigate to [http://localhost:8080/productpage](http://localhost:8080/productpage)

Refresh the page multiple times to see how the reviews service rotates between different versions.

## Visualize Your Service Mesh

### Step 1: Install Observability Tools

Install Kiali, Prometheus, Grafana, and Jaeger:

```bash
kubectl apply -f samples/addons
kubectl rollout status deployment/kiali -n istio-system
```

### Step 2: Access the Kiali Dashboard

Launch the Kiali dashboard:

```bash
istioctl dashboard kiali
```

### Step 3: Generate Traffic

To see trace data, generate traffic to the application:

```bash
for i in $(seq 1 100); do curl -s -o /dev/null "http://localhost:8080/productpage"; done
```

In the Kiali dashboard:
1. Select "Graph" from the left navigation menu
2. Choose "default" from the Namespace dropdown
3. Explore the service mesh topology and traffic flow

## Next Steps

After completing this getting started guide, explore these Istio features:

- [Request routing](https://istio.io/latest/docs/tasks/traffic-management/request-routing/)
- [Fault injection](https://istio.io/latest/docs/tasks/traffic-management/fault-injection/)
- [Traffic shifting](https://istio.io/latest/docs/tasks/traffic-management/traffic-shifting/)
- [Querying metrics](https://istio.io/latest/docs/tasks/observability/metrics/querying-metrics/)
- [Visualizing metrics](https://istio.io/latest/docs/tasks/observability/metrics/using-istio-dashboard/)
- [Accessing external services](https://istio.io/latest/docs/tasks/traffic-management/egress/egress-control/)

## Preparing for Production

Before deploying Istio in production, review:

- [Deployment models](https://istio.io/latest/docs/ops/deployment/deployment-models/)
- [Deployment best practices](https://istio.io/latest/docs/ops/best-practices/deployment/)
- [Pod requirements](https://istio.io/latest/docs/ops/deployment/application-requirements/)
- [General installation instructions](https://istio.io/latest/docs/setup/)

## Uninstalling Istio

To clean up, follow these steps:

1. Delete the Bookinfo application:
   ```bash
   kubectl delete -f samples/bookinfo/platform/kube/bookinfo.yaml
   ```

2. Delete the Gateway:
   ```bash
   kubectl delete -f samples/bookinfo/gateway-api/bookinfo-gateway.yaml
   ```

3. Delete the addons:
   ```bash
   kubectl delete -f samples/addons
   ```

4. Uninstall Istio:
   ```bash
   istioctl uninstall -y --purge
   ```

5. Remove the istio-system namespace:
   ```bash
   kubectl delete namespace istio-system
   ```

6. Remove the automatic injection label:
   ```bash
   kubectl label namespace default istio-injection-
   ```

7. Remove the Gateway API CRDs:
   ```bash
   kubectl kustomize "github.com/kubernetes-sigs/gateway-api/config/crd?ref=v1.3.0-rc.1" | kubectl delete -f -
   ```

## Conclusion

You've now successfully installed Istio, deployed a sample application, and explored basic service mesh functionality. Istio provides powerful capabilities for managing, securing, and observing microservices in Kubernetes environments.

For more information and community support, visit the [Istio website](https://istio.io/) and join the [Istio community](https://istio.io/get-involved/).
