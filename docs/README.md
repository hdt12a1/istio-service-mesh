# Istio Service Mesh Documentation

This documentation provides comprehensive guides for understanding, installing, and configuring Istio service mesh in your Kubernetes environment.

## Table of Contents

### Concepts
- [Service Mesh Introduction](concepts/service-mesh-introduction.md) - Basic concepts and benefits of service mesh
- [Service Mesh Architecture](concepts/service-mesh-architecture.md) - Detailed architecture of service mesh components
- [Istio Service Mesh](concepts/istio-service-mesh.md) - Overview of Istio-specific implementation
- [Istio Sidecar Traffic Flow](concepts/istio-sidecar-traffic-flow.md) - How traffic flows through Istio sidecars

### Security
- [mTLS and Peer Authentication](security/istio-mtls-peer-authentication.md) - Understanding mutual TLS authentication
- [mTLS Modes Detailed](security/istio-mtls-modes-detailed.md) - Deep dive into different mTLS modes
- [Permissive mTLS Mode](security/istio-permissive-mtls-mode-detailed.md) - How permissive mode works with mixed traffic
- [Auto mTLS](security/istio-auto-mtls-detailed.md) - Automatic mTLS configuration in Istio

### Traffic Management
- [Istio Gateway Routes](traffic-management/istio-gateway-routes.md) - Configuring ingress with Istio Gateways
- [Kubernetes Gateway API](traffic-management/kubernetes-gateway-api.md) - Using the Kubernetes Gateway API with Istio

### Observability
- [Prometheus Observability](observability/istio-prometheus-observability.md) - Metrics collection with Prometheus
- [Jaeger Distributed Tracing](observability/istio-jaeger-distributed-tracing.md) - Distributed tracing with Jaeger
- [Envoy Filter Chain Inspection](observability/istio-envoy-filter-chain-inspection.md) - Inspecting Envoy proxy configurations
- [Kiali EKS Token Authentication](observability/kiali-eks-token-authentication.md) - Setting up token authentication for Kiali in EKS
- [Kiali Ingress Configuration](observability/kiali-ingress-configuration.md) - Exposing Kiali through Kubernetes Ingress

### Installation
- [Istio Getting Started](installation/istio-getting-started.md) - Quick start guide for Istio installation
- [Service Mesh Configuration Example](installation/istio-service-mesh-configuration-example.md) - Complete example of configuring a service mesh

## How to Use This Documentation

1. **New to Service Mesh?** Start with the [Service Mesh Introduction](concepts/service-mesh-introduction.md) and [Istio Service Mesh](concepts/istio-service-mesh.md) documents.

2. **Ready to Install?** Follow the [Istio Getting Started](installation/istio-getting-started.md) guide.

3. **Need to Configure Security?** Check the documents in the Security section, starting with [mTLS and Peer Authentication](security/istio-mtls-peer-authentication.md).

4. **Setting up Observability?** Refer to the Observability section for guides on Prometheus, Jaeger, and Kiali.

5. **Configuring Traffic?** The Traffic Management section provides detailed information on routing and gateway configuration.

## Additional Resources

- [Istio Official Documentation](https://istio.io/latest/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Envoy Proxy Documentation](https://www.envoyproxy.io/docs/envoy/latest/)
