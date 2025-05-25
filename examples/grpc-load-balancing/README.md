# gRPC Load Balancing with Istio

This example demonstrates how to use Istio to load balance gRPC traffic across multiple service instances. It includes a simple Python gRPC Product Service with both server and client components.

## Overview

The example consists of:

1. A gRPC Product Service with 3 replicas
2. Istio configuration for optimal gRPC load balancing
3. A client to test the load distribution

The service includes server ID information in responses to demonstrate which instance handled each request.

## Directory Structure

```
grpc-load-balancing/
├── product-service/         # Service implementation
│   ├── product.proto        # gRPC service definition
│   ├── server.py            # Server implementation
│   ├── client.py            # Client for testing
│   ├── Dockerfile           # Server Docker image
│   ├── client.Dockerfile    # Client Docker image
│   └── requirements.txt     # Python dependencies
└── kubernetes/              # Kubernetes & Istio configuration
    ├── product-service.yaml # Service deployment
    ├── istio-config.yaml    # Istio routing & load balancing
    └── client-job.yaml      # Test client job
```

## Building and Deploying

### 1. Build the Docker Images

```bash
# Navigate to the product-service directory
cd product-service

# Build the server image
docker build -t product-service:v1 .

# Build the client image
docker build -t product-client:v1 -f client.Dockerfile .

# If using minikube, load the images
minikube image load product-service:v1
minikube image load product-client:v1
```

### 2. Deploy to Kubernetes with Istio

Ensure Istio is installed in your cluster and injection is enabled for your namespace:

```bash
# Enable Istio injection in your namespace
kubectl label namespace default istio-injection=enabled

# Deploy the product service
kubectl apply -f kubernetes/product-service.yaml

# Apply Istio configuration
kubectl apply -f kubernetes/istio-config.yaml
```

### 3. Verify the Deployment

```bash
# Check that all pods are running
kubectl get pods

# Verify the service
kubectl get svc product-service
```

## Testing Load Balancing

### Run the Client Job

```bash
# Run the client job to test load balancing
kubectl apply -f kubernetes/client-job.yaml

# Check the logs to see the distribution of requests
kubectl logs job/grpc-client-job
```

### Expected Results

The client will send 300 requests to the service and report which server instance handled each request. With the Istio configuration in place, you should see a relatively even distribution of requests across the three server instances.

Without proper load balancing settings, one instance might handle most requests. With our settings:
- `http2MaxRequests: 1000`
- `maxRequestsPerConnection: 100`
- `loadBalancer.simple: LEAST_CONN`

You should see a much more balanced distribution.

## Monitoring with Istio

You can also use Istio's observability tools to monitor the traffic:

```bash
# Open Kiali dashboard
istioctl dashboard kiali

# Open Grafana dashboard
istioctl dashboard grafana
```

In Kiali, navigate to the graph view to see the traffic distribution between the client and the product service instances.

## Explanation of Load Balancing Settings

The key settings in `istio-config.yaml` that enable effective gRPC load balancing are:

```yaml
trafficPolicy:
  loadBalancer:
    simple: LEAST_CONN
  connectionPool:
    http:
      http2MaxRequests: 1000
      maxRequestsPerConnection: 100
```

- **LEAST_CONN**: Routes requests to the backend with the fewest active connections
- **http2MaxRequests**: Limits concurrent requests to a backend
- **maxRequestsPerConnection**: Forces connections to cycle after this many requests

These settings ensure that gRPC traffic is evenly distributed across all instances, even though gRPC uses long-lived HTTP/2 connections.

## Cleaning Up

```bash
# Delete the client job
kubectl delete -f kubernetes/client-job.yaml

# Delete the Istio configuration
kubectl delete -f kubernetes/istio-config.yaml

# Delete the product service
kubectl delete -f kubernetes/product-service.yaml
```
