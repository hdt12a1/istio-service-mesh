# Kiali Installation Guide

This guide explains how to install Kiali in a Kubernetes cluster with Istio using Helm charts. There are two approaches to installing Kiali:

1. **Using the Kiali Operator** - Recommended for production environments and when you need multiple Kiali instances
2. **Direct Kiali Server Installation** - Simpler approach for development or when you don't need the operator

## Prerequisites

Before installing Kiali, ensure you have:

- A Kubernetes cluster with Istio installed
- [Helm](https://helm.sh/docs/intro/install/) (version 3.2 or later) installed
- `kubectl` configured to access your cluster
- Prometheus installed and configured (required for Kiali to function)

## 1. Installation Using the Kiali Operator

The operator pattern provides advanced management capabilities for Kiali, including:
- Automatic updates
- Multiple Kiali instances
- Advanced configuration management

### Step 1: Add the Kiali Helm Repository

```bash
helm repo add kiali https://kiali.org/helm-charts
helm repo update
```

### Step 2: Install the Kiali Operator

```bash
# Create the namespace for the operator
kubectl create namespace kiali-operator

# Install the operator using our custom chart
helm install kiali-operator ./install/kiali-operator \
  --namespace kiali-operator
```

This will:
1. Install the Kiali Operator in the `kiali-operator` namespace
2. Create a Kiali CR in the `istio-system` namespace (because `cr.create: true` in our values)
3. Deploy the Kiali server based on the CR configuration

### Step 3: Verify the Installation

```bash
# Check the operator deployment
kubectl get pods -n kiali-operator

# Check the Kiali deployment
kubectl get pods -n istio-system -l app=kiali
```

### Step 4: Access Kiali

```bash
# Port-forward the Kiali service
kubectl port-forward svc/kiali -n istio-system 20001:20001
```

Then access Kiali at: http://localhost:20001

## 2. Direct Kiali Server Installation

For simpler deployments, you can install Kiali directly without the operator.

### Step 1: Add the Kiali Helm Repository (if not already added)

```bash
helm repo add kiali https://kiali.org/helm-charts
helm repo update
```

### Step 2: Install Kiali Server

```bash
# Create the namespace if it doesn't exist
kubectl create namespace istio-system --dry-run=client -o yaml | kubectl apply -f -

# Install Kiali server using our custom chart
helm install kiali-server ./install/kiali-server \
  --namespace istio-system
```

### Step 3: Verify the Installation

```bash
# Check the Kiali deployment
kubectl get pods -n istio-system -l app=kiali
```

### Step 4: Access Kiali

```bash
# Port-forward the Kiali service
kubectl port-forward svc/kiali -n istio-system 20001:20001
```

Then access Kiali at: http://localhost:20001

## Customizing the Installation

### Operator Installation Customization

The key configuration options in the `values.yaml` for the operator installation:

```yaml
kiali-operator:
  cr:
    create: true                # Whether to create a Kiali CR automatically
    namespace: istio-system     # Namespace for the Kiali CR
    spec:
      auth:
        strategy: "anonymous"   # Authentication strategy
      deployment:
        accessible_namespaces:
          - "**"                # Namespaces Kiali can access
      external_services:
        prometheus:
          url: "http://prometheus-server.istio-system:9090"  # Prometheus URL
```

### Direct Server Installation Customization

The key configuration options in the `values.yaml` for the direct server installation:

```yaml
kiali-server:
  auth:
    strategy: "anonymous"       # Authentication strategy
  deployment:
    accessible_namespaces:
      - "**"                    # Namespaces Kiali can access
  external_services:
    prometheus:
      url: "http://prometheus-server.istio-system:9090"  # Prometheus URL
```

## Uninstalling Kiali

### Uninstall Operator-based Installation

```bash
# Uninstall the Kiali CR first (if it was created by the operator)
kubectl delete kiali kiali -n istio-system

# Then uninstall the operator
helm uninstall kiali-operator -n kiali-operator
```

### Uninstall Direct Server Installation

```bash
helm uninstall kiali-server -n istio-system
```

## Troubleshooting

### Common Issues

1. **Kiali can't connect to Prometheus**:
   - Verify Prometheus is running: `kubectl get pods -n istio-system -l app=prometheus`
   - Check the URL in the Kiali configuration matches your Prometheus service

2. **Authentication issues**:
   - If using a strategy other than "anonymous", ensure the authentication provider is properly configured

3. **Missing service mesh data**:
   - Ensure Istio is properly installed and running
   - Verify that Prometheus is scraping Istio metrics

### Viewing Logs

```bash
# For operator installation, check operator logs
kubectl logs -n kiali-operator -l app=kiali-operator

# Check Kiali server logs
kubectl logs -n istio-system -l app=kiali
```

## Additional Resources

- [Kiali Official Documentation](https://kiali.io/docs/)
- [Kiali GitHub Repository](https://github.com/kiali/kiali)
- [Kiali Helm Charts Repository](https://github.com/kiali/helm-charts)
