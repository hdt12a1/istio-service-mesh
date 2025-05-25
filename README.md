# Istio Service Mesh Project

This repository contains comprehensive documentation, installation guides, and configuration examples for implementing Istio Service Mesh in Kubernetes environments.

## Project Overview

This project provides a complete toolkit for understanding, deploying, and managing Istio service mesh, with a focus on:

- Detailed conceptual explanations
- Step-by-step installation guides
- Security configuration with mTLS
- Traffic management patterns
- Observability setup (Prometheus, Jaeger, Kiali)
- Production-ready configuration examples

## Repository Structure

```
service-mesh/
├── docs/                      # Documentation organized by topic
│   ├── concepts/              # Fundamental service mesh concepts
│   ├── installation/          # Installation and configuration guides
│   ├── observability/         # Monitoring, tracing, and visualization
│   ├── security/              # mTLS and authentication
│   └── traffic-management/    # Routing and gateway configuration
│
├── install/                   # Installation resources and Helm charts
│   ├── istio/                 # Istio installation configurations
│   ├── jaeger/                # Jaeger distributed tracing Helm chart
│   ├── kiali-operator/        # Kiali operator Helm chart
│   ├── kiali-server/          # Kiali server Helm chart
│   └── prometheus/            # Prometheus monitoring Helm chart
│
└── examples/                  # Example applications and configurations
```

## Getting Started

### Prerequisites

Before using this project, ensure you have:

- A Kubernetes cluster (v1.19+)
- kubectl configured to access your cluster
- Helm 3.x installed
- Basic understanding of Kubernetes concepts

### Quick Start

1. **Read the Conceptual Overview**:
   - Start with [Service Mesh Introduction](docs/concepts/service-mesh-introduction.md)
   - Review [Istio Service Mesh Architecture](docs/concepts/service-mesh-architecture.md)

2. **Install Istio**:
   - Follow the [Istio Installation Guide](docs/installation/istio-getting-started.md)
   - Use the provided Helm charts in the `install/istio` directory

3. **Configure Security**:
   - Implement mTLS using guides in the `docs/security` directory
   - Start with [mTLS and Peer Authentication](docs/security/istio-mtls-peer-authentication.md)

4. **Set Up Observability**:
   - Deploy Prometheus using the Helm chart in `install/prometheus`
   - Deploy Jaeger using the Helm chart in `install/jaeger`
   - Deploy Kiali using the Helm chart in `install/kiali-server`
   - Follow the integration guides in the `docs/observability` directory

5. **Implement Traffic Management**:
   - Use the patterns described in `docs/traffic-management`
   - Apply the example configurations from the `examples` directory

## Documentation Guide

The documentation is organized to support both learning and reference use cases:

### For Learning Path (Recommended Order)

1. **Understanding Service Mesh**
   - [Service Mesh Introduction](docs/concepts/service-mesh-introduction.md)
   - [Service Mesh Architecture](docs/concepts/service-mesh-architecture.md)
   - [Istio Service Mesh](docs/concepts/istio-service-mesh.md)
   - [Istio Sidecar Traffic Flow](docs/concepts/istio-sidecar-traffic-flow.md)

2. **Installation and Basic Setup**
   - [Istio Getting Started](docs/installation/istio-getting-started.md)
   - [Service Mesh Configuration Example](docs/installation/istio-service-mesh-configuration-example.md)

3. **Security Configuration**
   - [mTLS and Peer Authentication](docs/security/istio-mtls-peer-authentication.md)
   - [mTLS Modes Detailed](docs/security/istio-mtls-modes-detailed.md)
   - [Permissive mTLS Mode](docs/security/istio-permissive-mtls-mode-detailed.md)
   - [Auto mTLS](docs/security/istio-auto-mtls-detailed.md)

4. **Observability Setup**
   - [Prometheus Observability](docs/observability/istio-prometheus-observability.md)
   - [Jaeger Distributed Tracing](docs/observability/istio-jaeger-distributed-tracing.md)
   - [Kiali Setup and Configuration](docs/observability/kiali-ingress-configuration.md)

5. **Advanced Traffic Management**
   - [Istio Gateway Routes](docs/traffic-management/istio-gateway-routes.md)
   - [Kubernetes Gateway API](docs/traffic-management/kubernetes-gateway-api.md)

### For Reference Use

- **Troubleshooting**: See [Envoy Filter Chain Inspection](docs/observability/istio-envoy-filter-chain-inspection.md)
- **EKS-Specific Guidance**: See [Kiali EKS Token Authentication](docs/observability/kiali-eks-token-authentication.md)
- **Complete Example**: See [Service Mesh Configuration Example](docs/installation/istio-service-mesh-configuration-example.md)

## Installation Resources

The `install` directory contains Helm charts and configuration files for deploying:

- **Istio**: Core service mesh components
- **Prometheus**: Metrics collection and storage
- **Jaeger**: Distributed tracing
- **Kiali**: Service mesh visualization and management

Each component has a dedicated directory with:
- `Chart.yaml`: Helm chart definition
- `values.yaml`: Default configuration values
- Additional documentation specific to that component

## Examples

The `examples` directory contains sample applications and configurations that demonstrate:

- Basic service mesh patterns
- Security configurations
- Traffic routing scenarios
- Observability integrations

## Contributing

Contributions to this project are welcome! Please consider:

1. Adding new documentation for advanced scenarios
2. Improving existing guides with clearer explanations
3. Updating Helm charts for newer versions of components
4. Adding new examples for specific use cases

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Istio community for creating an amazing service mesh
- Kubernetes SIG-Network for the Gateway API
- The observability projects (Prometheus, Jaeger, Kiali) for their tools
