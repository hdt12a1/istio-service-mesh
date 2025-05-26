# Genesis Services Example

This example demonstrates how to configure and deploy service-a and service-b in the genesis namespace with Istio, focusing on gRPC communication between services.

## Overview

- **service-a**: A frontend service that receives requests from external clients
- **service-b**: A backend service that is called by service-a
- Both services communicate via gRPC and are secured with mTLS

## Directory Structure

```
genesis-services/
├── README.md
├── gateway.yaml
├── service-a/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── destination-rule.yaml
├── service-b/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── destination-rule.yaml
├── routes/
│   ├── grpc-route.yaml
│   └── http-route.yaml
└── security/
    ├── peer-authentication.yaml
    └── authorization-policy.yaml
```

## Deployment Instructions

1. Apply namespace and enable Istio injection:
   ```bash
   kubectl create namespace genesis
   kubectl label namespace genesis istio-injection=enabled
   ```

2. Deploy the services:
   ```bash
   kubectl apply -f service-a/
   kubectl apply -f service-b/
   ```

3. Deploy the gateway and routes:
   ```bash
   kubectl apply -f gateway.yaml
   kubectl apply -f routes/
   ```

4. Apply security policies:
   ```bash
   kubectl apply -f security/
   ```

## Testing the Services

### Internal Communication (from service-a pod)

```bash
# Get a shell in the service-a pod
kubectl exec -it -n genesis $(kubectl get pod -n genesis -l app=service-a -o jsonpath='{.items[0].metadata.name}') -- sh

# Test HTTP endpoint
curl http://service-b:8080/healthcheck/readiness

# Test gRPC endpoint
grpcurl service-b:8080 com.example.ServiceB/SomeMethod
```

### External Access

```bash
# Get the gateway IP
export GATEWAY_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test HTTP endpoint
curl -H "Host: api.example.com" https://$GATEWAY_IP/service-a/endpoint

# Test gRPC endpoint
grpcurl -insecure -authority api.example.com $GATEWAY_IP:443 com.example.ServiceA/SomeMethod
```

## Troubleshooting

See the [Service Mesh Communication Patterns](../../docs/architecture/service-mesh-communication-patterns.md) document for detailed troubleshooting steps and architecture explanation.
