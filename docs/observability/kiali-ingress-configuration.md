# Configuring Ingress for Kiali in EKS

This guide explains how to expose Kiali through an Ingress in an Amazon EKS cluster. Using Ingress provides several advantages over LoadBalancer services, including path-based routing, TLS termination, and the ability to host multiple services on a single load balancer.

## Prerequisites

Before configuring Ingress for Kiali, ensure you have:

1. A running EKS cluster with Istio installed
2. Kiali installed in the cluster
3. An Ingress controller installed (NGINX, ALB, etc.)
4. (Optional) A domain name and DNS configuration

## Ingress Configuration Options

There are two main approaches to exposing Kiali via Ingress:

1. **Using Kiali's built-in Ingress configuration** (recommended for Helm installations)
2. **Creating a separate Ingress resource** (useful for custom configurations)

## Option 1: Using Kiali's Built-in Ingress Configuration

### Step 1: Update Kiali Server Values

If you're using the Kiali server Helm chart, modify the `values.yaml` file:

```yaml
kiali-server:
  deployment:
    ingress:
      enabled: true
      class_name: "nginx"  # Use "alb" for AWS ALB Ingress Controller
      hosts:
        - host: kiali.example.com  # Replace with your domain
          paths:
            - path: /
              path_type: Prefix
```

For AWS Application Load Balancer (ALB), you might want to add annotations:

```yaml
kiali-server:
  deployment:
    ingress:
      enabled: true
      class_name: "alb"
      additional_labels: {}
      annotations:
        kubernetes.io/ingress.class: alb
        alb.ingress.kubernetes.io/scheme: internet-facing
        alb.ingress.kubernetes.io/target-type: ip
      hosts:
        - host: kiali.example.com
          paths:
            - path: /
              path_type: Prefix
```

### Step 2: Apply the Configuration

```bash
helm upgrade --install kiali-server ./install/kiali-server \
  --namespace istio-system
```

## Option 2: Creating a Separate Ingress Resource

If you prefer to manage the Ingress separately or need more customization:

### Step 1: Create an Ingress Manifest

Create a file named `kiali-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kiali-ingress
  namespace: istio-system
  annotations:
    kubernetes.io/ingress.class: nginx  # Or "alb" for AWS ALB
    # For ALB Ingress Controller
    # alb.ingress.kubernetes.io/scheme: internet-facing
    # alb.ingress.kubernetes.io/target-type: ip
    # For NGINX Ingress Controller
    nginx.ingress.kubernetes.io/backend-protocol: HTTP
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: kiali.example.com  # Replace with your domain
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: kiali
            port:
              number: 20001
```

### Step 2: Apply the Ingress

```bash
kubectl apply -f kiali-ingress.yaml
```

## Configuring TLS (HTTPS)

### Option 1: Using AWS Certificate Manager (ACM) with ALB

For ALB Ingress Controller with ACM:

```yaml
metadata:
  annotations:
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:region:account-id:certificate/certificate-id
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
```

### Option 2: Using TLS Secret with NGINX Ingress

```yaml
spec:
  tls:
  - hosts:
    - kiali.example.com
    secretName: kiali-tls-secret
```

Create the TLS secret:

```bash
kubectl create secret tls kiali-tls-secret \
  --key /path/to/private-key.pem \
  --cert /path/to/certificate.pem \
  -n istio-system
```

## Using Istio Gateway Instead of Kubernetes Ingress

If you're using Istio, you might prefer to use Istio Gateway and VirtualService instead of Kubernetes Ingress:

### Step 1: Create Gateway and VirtualService

Create a file named `kiali-gateway.yaml`:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: kiali-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "kiali.example.com"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: kiali-vs
  namespace: istio-system
spec:
  hosts:
  - "kiali.example.com"
  gateways:
  - kiali-gateway
  http:
  - route:
    - destination:
        host: kiali
        port:
          number: 20001
```

### Step 2: Apply the Gateway and VirtualService

```bash
kubectl apply -f kiali-gateway.yaml
```

## Verifying the Ingress Configuration

### Check Ingress Status

```bash
kubectl get ingress -n istio-system
```

### For ALB Ingress Controller

```bash
kubectl get ingress kiali-ingress -n istio-system -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### For NGINX Ingress Controller

```bash
kubectl get svc -n ingress-nginx
```

## Troubleshooting

### Common Issues

1. **Ingress Not Working**
   - Check if the Ingress controller pods are running
   - Verify the Ingress resource is correctly configured
   - Check if the service is accessible within the cluster

2. **TLS Issues**
   - Verify the TLS certificate is valid and properly configured
   - Check if the secret exists and is correctly referenced

3. **Routing Issues**
   - Ensure the host and path configuration matches your requirements
   - Check if the service name and port are correct

### Diagnostic Commands

```bash
# Check Ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Check Ingress status
kubectl describe ingress kiali-ingress -n istio-system

# Test connectivity to Kiali service
kubectl run -it --rm curl --image=curlimages/curl -n istio-system -- curl -v http://kiali:20001
```

## Best Practices

1. **Use HTTPS**
   - Always configure TLS for production environments
   - Use AWS Certificate Manager for ALB Ingress

2. **Configure Authentication**
   - Consider using authentication at the Ingress level
   - For NGINX Ingress, you can use basic auth or OAuth2 proxy

3. **Set Resource Limits**
   - Configure appropriate resource limits for the Ingress controller

4. **Monitor Ingress**
   - Set up monitoring for your Ingress controller
   - Monitor Kiali access logs

## AWS-Specific Considerations

### Using AWS ALB Ingress Controller

The AWS ALB Ingress Controller creates Application Load Balancers automatically based on Ingress resources:

1. **Installation**:
   ```bash
   helm repo add eks https://aws.github.io/eks-charts
   helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
     -n kube-system \
     --set clusterName=your-cluster-name \
     --set serviceAccount.create=false \
     --set serviceAccount.name=aws-load-balancer-controller
   ```

2. **IAM Policy**:
   Ensure the ALB Ingress Controller has the necessary IAM permissions.

3. **Annotations**:
   ```yaml
   annotations:
     kubernetes.io/ingress.class: alb
     alb.ingress.kubernetes.io/scheme: internet-facing
     alb.ingress.kubernetes.io/target-type: ip
     alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
     alb.ingress.kubernetes.io/actions.ssl-redirect: '{"Type": "redirect", "RedirectConfig": {"Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}}'
   ```

### Using Network Load Balancer (NLB)

For NLB with Istio Gateway:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: istio-ingressgateway
  namespace: istio-system
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-internal: "false"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    name: http
  - port: 443
    name: https
  selector:
    istio: ingressgateway
```

## Conclusion

Configuring Ingress for Kiali in EKS provides a secure and scalable way to access the Kiali UI. Whether you use the built-in Ingress configuration in the Helm chart or create a separate Ingress resource, you can customize the setup to meet your specific requirements.

For production environments, consider using HTTPS, implementing authentication, and following AWS best practices for load balancer configuration.
