# Istio PERMISSIVE mTLS Mode: Detailed Request Flow

## Introduction

PERMISSIVE mode is one of Istio's mutual TLS (mTLS) configurations that allows services to accept both mTLS and plain text traffic simultaneously. This document provides an in-depth explanation of how PERMISSIVE mode works, with detailed flow diagrams showing exactly what happens when different types of clients make requests to a service configured with PERMISSIVE mode.

## What is PERMISSIVE Mode?

PERMISSIVE mode is a flexible mTLS configuration that:

- Accepts both encrypted mTLS traffic and unencrypted plain text traffic
- Allows services to communicate with both mesh and non-mesh clients
- Provides a transition path when migrating to mTLS
- Maintains backward compatibility while enabling security where possible

```mermaid
graph TD
    subgraph "PERMISSIVE Mode Behavior"
        PM[PERMISSIVE Mode Service]
        
        mTLS[mTLS Client] -->|Encrypted + Authenticated| PM
        Plain[Plain Text Client] -->|Unencrypted| PM
        
        PM -->|Accepts| mTLS
        PM -->|Accepts| Plain
    end
    
    style PM fill:#bbf,stroke:#333,stroke-width:2px
    style mTLS fill:#bfb,stroke:#333,stroke-width:1px
    style Plain fill:#fdb,stroke:#333,stroke-width:1px
```

## Configuring PERMISSIVE Mode

PERMISSIVE mode is configured using the PeerAuthentication resource:

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: your-namespace  # Apply to a namespace
spec:
  mtls:
    mode: PERMISSIVE
```

You can also apply it to specific workloads:

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: service-specific
  namespace: your-namespace
spec:
  selector:
    matchLabels:
      app: your-service
  mtls:
    mode: PERMISSIVE
```

## Detailed Request Flows in PERMISSIVE Mode

Let's examine in detail what happens when different types of clients make requests to a service configured with PERMISSIVE mode.

### Scenario 1: Mesh Client to PERMISSIVE Service (mTLS Flow)

When a client within the mesh (with an Istio sidecar) makes a request to a service configured with PERMISSIVE mode, the communication automatically uses mTLS:

```mermaid
sequenceDiagram
    participant App A as Application A
    participant Proxy A as Envoy Proxy A
    participant Proxy B as Envoy Proxy B
    participant App B as Application B (PERMISSIVE)
    participant Istiod as Istiod (Control Plane)
    
    Note over App A,App B: Both services have Istio sidecars
    
    App A->>Proxy A: 1. Make request to Service B
    
    Proxy A->>Istiod: 2. Request service discovery for Service B
    Istiod->>Proxy A: 3. Return Service B endpoints
    
    Proxy A->>Istiod: 4. Request client certificate
    Istiod->>Proxy A: 5. Issue client certificate
    
    Note over Proxy A,Proxy B: mTLS Handshake
    Proxy A->>Proxy B: 6. Client Hello (initiate TLS)
    Proxy B->>Proxy A: 7. Server Hello + Server Certificate
    Proxy A->>Proxy B: 8. Client Certificate
    
    Note over Proxy A,Proxy B: Certificate Validation
    Proxy B->>Istiod: 9. Validate client certificate
    Istiod->>Proxy B: 10. Certificate validation result
    
    Note over Proxy A,Proxy B: Secure Communication Established
    Proxy A->>Proxy B: 11. Encrypted request
    
    Proxy B->>App B: 12. Forward request to application
    App B->>Proxy B: 13. Response
    
    Proxy B->>Proxy A: 14. Encrypted response
    Proxy A->>App A: 15. Forward response to Application A
```

**Key Points in this Flow:**

1. **Automatic mTLS Negotiation**: The client sidecar automatically attempts mTLS
2. **Certificate Exchange**: Both proxies exchange and validate certificates
3. **Identity Verification**: The service validates the client's identity
4. **Transparent to Applications**: Both applications are unaware of the mTLS process
5. **End-to-End Encryption**: All traffic between the proxies is encrypted

### Scenario 2: Non-Mesh Client to PERMISSIVE Service (Plain Text Flow)

When a client without an Istio sidecar makes a request to a service configured with PERMISSIVE mode:

```mermaid
sequenceDiagram
    participant Non-Mesh Client
    participant K8s Service as Kubernetes Service
    participant Proxy B as Envoy Proxy B
    participant App B as Application B (PERMISSIVE)
    
    Note over Non-Mesh Client,App B: Client has no sidecar, Service B has PERMISSIVE mode
    
    Non-Mesh Client->>K8s Service: 1. Plain text request to Service B
    K8s Service->>Proxy B: 2. Forward to pod with Service B
    
    Note over Proxy B: Protocol Detection
    Proxy B->>Proxy B: 3. Detect plain text protocol
    
    Note over Proxy B: Filter Chain Selection
    Proxy B->>Proxy B: 4. Select plain text filter chain
    
    Proxy B->>App B: 5. Forward request to application
    App B->>Proxy B: 6. Response
    
    Proxy B->>K8s Service: 7. Plain text response
    K8s Service->>Non-Mesh Client: 8. Forward response to client
```

**Key Points in this Flow:**

1. **Protocol Detection**: The service proxy detects that the incoming request is plain text
2. **Filter Chain Selection**: The proxy selects the appropriate filter chain for plain text
3. **No Authentication**: No client identity verification occurs
4. **No Encryption**: Traffic remains unencrypted
5. **Backward Compatibility**: The service can still handle legacy clients

### Scenario 3: Mesh Client to External Service via PERMISSIVE Egress

When a mesh service communicates with an external service through an egress gateway with PERMISSIVE mode:

```mermaid
sequenceDiagram
    participant App A as Application A
    participant Proxy A as Envoy Proxy A
    participant Egress as Egress Gateway (PERMISSIVE)
    participant External as External Service
    participant Istiod as Istiod (Control Plane)
    
    App A->>Proxy A: 1. Request to external service
    
    Proxy A->>Istiod: 2. Check ServiceEntry for external service
    Istiod->>Proxy A: 3. Return routing information
    
    Note over Proxy A,Egress: Internal mTLS Communication
    Proxy A->>Egress: 4. Encrypted request to egress gateway
    
    Note over Egress,External: External Communication
    Egress->>Egress: 5. Apply TLS origination if configured
    Egress->>External: 6. Forward request (TLS or plain text)
    External->>Egress: 7. Response
    
    Note over Egress,Proxy A: Internal mTLS Communication
    Egress->>Proxy A: 8. Encrypted response
    Proxy A->>App A: 9. Forward response to application
```

**Key Points in this Flow:**

1. **Secure Internal Communication**: Traffic within the mesh uses mTLS
2. **Configurable External Security**: The egress gateway can be configured to use TLS for external communication
3. **Protocol Translation**: The gateway can translate between mTLS internally and other protocols externally
4. **Centralized External Access**: All external traffic goes through controlled gateways

### Scenario 4: Mixed Traffic with Auto mTLS

When auto mTLS is enabled with PERMISSIVE mode, Istio automatically detects whether the destination supports mTLS:

```mermaid
sequenceDiagram
    participant App A as Application A
    participant Proxy A as Envoy Proxy A
    participant Istiod as Istiod (Control Plane)
    participant Proxy B as Envoy Proxy B (PERMISSIVE)
    participant App B as Application B
    participant App C as Application C (No Sidecar)
    
    App A->>Proxy A: 1. Request to Service B
    
    Proxy A->>Istiod: 2. Service discovery for B
    Istiod->>Proxy A: 3. B has sidecar, use mTLS
    
    Note over Proxy A,Proxy B: mTLS Communication
    Proxy A->>Proxy B: 4. Encrypted request
    Proxy B->>App B: 5. Forward request
    App B->>Proxy B: 6. Response
    Proxy B->>Proxy A: 7. Encrypted response
    Proxy A->>App A: 8. Forward response
    
    App A->>Proxy A: 9. Request to Service C
    
    Proxy A->>Istiod: 10. Service discovery for C
    Istiod->>Proxy A: 11. C has no sidecar, use plain text
    
    Note over Proxy A,App C: Plain Text Communication
    Proxy A->>App C: 12. Plain text request
    App C->>Proxy A: 13. Response
    Proxy A->>App A: 14. Forward response
```

**Key Points in this Flow:**

1. **Automatic Protocol Selection**: Istio automatically chooses mTLS or plain text based on destination capabilities
2. **Dynamic Behavior**: The same client can use different security modes for different destinations
3. **Zero Configuration**: Developers don't need to specify the security mode for each destination
4. **Optimal Security**: Uses the highest security level supported by each service

## PERMISSIVE Mode Implementation Details

### Envoy Configuration

In PERMISSIVE mode, Istio configures the Envoy proxy with multiple filter chains to handle both mTLS and plain text traffic:

```yaml
# Simplified Envoy configuration (not directly user-configurable)
listener:
  filter_chains:
  # Filter chain for mTLS traffic
  - filter_chain_match:
      transport_protocol: "tls"
    transport_socket:
      name: envoy.transport_sockets.tls
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
        require_client_certificate: true
        validation_context:
          trusted_ca:
            filename: /etc/certs/root-cert.pem
  
  # Filter chain for plain text traffic
  - filter_chain_match:
      transport_protocol: "raw_buffer"
    # Plain text configuration
```

### Protocol Detection

Envoy uses protocol detection to determine whether incoming traffic is TLS or plain text:

1. **Initial Bytes Examination**: Examines the first few bytes of the connection
2. **TLS Detection**: Looks for the TLS handshake signature (0x16 0x03 0x01)
3. **Filter Chain Selection**: Routes to the appropriate filter chain based on the detected protocol
4. **Fallback Mechanism**: If detection fails, defaults to the plain text filter chain

## Observability in PERMISSIVE Mode

### Monitoring mTLS vs Plain Text Traffic

In PERMISSIVE mode, it's important to monitor the ratio of mTLS to plain text traffic:

```mermaid
graph LR
    subgraph "Monitoring PERMISSIVE Mode"
        A[Collect Metrics] --> B[Analyze Traffic Patterns]
        B --> C[Identify Plain Text Sources]
        C --> D[Plan Migration to STRICT]
    end
    
    style A fill:#bbf,stroke:#333,stroke-width:1px
    style B fill:#bfb,stroke:#333,stroke-width:1px
    style C fill:#fdb,stroke:#333,stroke-width:1px
    style D fill:#f9f,stroke:#333,stroke-width:1px
```

### Key Metrics to Monitor

1. **Connection Security Policy**:
   ```bash
   # Prometheus query to show ratio of mTLS vs plain text
   sum(istio_requests_total{connection_security_policy="mutual_tls"}) by (destination_service) / 
   sum(istio_requests_total) by (destination_service)
   ```

2. **TLS Handshake Errors**:
   ```bash
   # Prometheus query for TLS handshake failures
   sum(rate(envoy_cluster_ssl_handshake_error[5m])) by (pod)
   ```

### Visualization in Kiali

Kiali provides visual indicators for traffic security in PERMISSIVE mode:

- **Lock icons**: Show which connections are using mTLS
- **Color coding**: Different colors for secured vs unsecured connections
- **Security view**: Dedicated view showing the security status of all connections

## Use Cases for PERMISSIVE Mode

### 1. Gradual Migration to mTLS

```mermaid
graph LR
    A[Start: No mTLS] --> B[Deploy Istio]
    B --> C[Enable PERMISSIVE mode]
    C --> D[Monitor traffic patterns]
    D --> E[Update clients to use mTLS]
    E --> F[Verify all traffic uses mTLS]
    F --> G[Switch to STRICT mode]
    
    style A fill:#fdb,stroke:#333,stroke-width:1px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#f9f,stroke:#333,stroke-width:1px
```

### 2. Mixed Environment with External Clients

PERMISSIVE mode allows services to accept traffic from both:
- Internal services within the mesh (using mTLS)
- External clients outside the mesh (using plain text)

This is useful for services that need to be accessible both internally and externally.

### 3. Compatibility with Legacy Systems

When integrating with legacy systems that cannot support mTLS, PERMISSIVE mode allows:
- Modern services to communicate securely with each other
- Legacy systems to continue functioning without modification

### 4. Development and Testing

During development and testing, PERMISSIVE mode provides flexibility:
- Developers can access services directly without mTLS configuration
- Test tools can probe services without complex certificate setup
- Production-like security can still be tested with mTLS clients

## Best Practices for PERMISSIVE Mode

### 1. Monitoring and Visibility

- **Track mTLS percentage**: Monitor the percentage of traffic using mTLS vs plain text
- **Set up alerts**: Create alerts for unexpected plain text traffic
- **Regular audits**: Periodically review which clients are using plain text

### 2. Client Configuration

- **Prefer mTLS for mesh clients**: Configure mesh clients to use mTLS when possible
- **Document exceptions**: Maintain documentation of clients that require plain text
- **Update clients incrementally**: Gradually update clients to support mTLS

### 3. Security Considerations

- **Treat as temporary**: Consider PERMISSIVE mode as a transitional state, not permanent
- **Limit scope**: Apply PERMISSIVE mode only where needed, not mesh-wide
- **Combine with other security**: Use additional security measures for sensitive services

### 4. Migration Planning

- **Set timeline**: Establish a timeline for transitioning to STRICT mode
- **Phased approach**: Migrate services to STRICT mode in phases
- **Test thoroughly**: Validate STRICT mode in non-production before applying to production

## Troubleshooting PERMISSIVE Mode

### Common Issues

1. **Inconsistent Security Behavior**:
   - **Symptom**: Some requests use mTLS, others don't, unpredictably
   - **Cause**: Misconfigured clients or auto mTLS issues
   - **Solution**: Check client DestinationRules and auto mTLS settings

2. **Performance Overhead**:
   - **Symptom**: Higher latency compared to plain text or STRICT mode
   - **Cause**: Protocol detection adds overhead
   - **Solution**: Monitor performance and consider moving to STRICT mode

3. **Certificate Errors with mTLS Clients**:
   - **Symptom**: mTLS clients fail with certificate errors
   - **Cause**: Certificate misconfiguration or trust issues
   - **Solution**: Check certificate validity and trust configuration

### Debugging Commands

```bash
# Check if traffic to a service is using mTLS
istioctl x describe service <service>.<namespace>

# View TLS configuration for a pod
istioctl proxy-config listener <pod-name>.<namespace> --port <port> -o json

# Check mTLS policy applied to a workload
istioctl x auth -n <namespace> <pod-name>

# View Envoy stats for TLS
kubectl exec <pod-name> -c istio-proxy -- pilot-agent request GET stats | grep ssl
```

## Transitioning from PERMISSIVE to STRICT Mode

### Step-by-Step Migration Plan

```mermaid
graph TD
    A[1. Enable PERMISSIVE mode] --> B[2. Monitor traffic patterns]
    B --> C{3. All traffic using mTLS?}
    C -->|No| D[4a. Identify plain text clients]
    D --> E[5a. Update clients to use mTLS]
    E --> B
    C -->|Yes| F[4b. Test STRICT mode in staging]
    F --> G{5b. Tests successful?}
    G -->|No| H[6a. Fix issues]
    H --> F
    G -->|Yes| I[6b. Apply STRICT mode to production]
    I --> J[7. Monitor for issues]
    
    style A fill:#bbf,stroke:#333,stroke-width:2px
    style I fill:#f9f,stroke:#333,stroke-width:2px
```

### Verification Before Switching

Before transitioning from PERMISSIVE to STRICT mode:

1. **Verify mTLS usage**: Ensure all traffic is already using mTLS
   ```bash
   # Check for any plain text traffic
   kubectl exec -it <pod-name> -c istio-proxy -- pilot-agent request GET stats | grep -E "ssl.handshake|http.inbound"
   ```

2. **Test with temporary policy**: Apply a temporary STRICT policy to a test service
   ```yaml
   apiVersion: security.istio.io/v1beta1
   kind: PeerAuthentication
   metadata:
     name: strict-test
     namespace: test
   spec:
     selector:
       matchLabels:
         app: test-service
     mtls:
       mode: STRICT
   ```

3. **Validate all clients**: Ensure all clients can still access the service

## Conclusion

PERMISSIVE mTLS mode in Istio provides a flexible approach to service mesh security, allowing services to accept both mTLS and plain text traffic. This flexibility is particularly valuable during migration to mTLS, in mixed environments, and when working with legacy systems.

Understanding the detailed request flows in PERMISSIVE mode helps you:
- Visualize how different types of clients interact with your services
- Plan your migration strategy to stronger security
- Troubleshoot issues that may arise during implementation
- Make informed decisions about your service mesh security configuration

While PERMISSIVE mode is an excellent transitional tool, the ultimate goal for most production environments should be to move to STRICT mode once all services and clients support mTLS, to ensure the highest level of security across your service mesh.

## Additional Resources

- [Istio Authentication Policy](https://istio.io/latest/docs/reference/config/security/peer_authentication/)
- [Mutual TLS Migration](https://istio.io/latest/docs/tasks/security/authentication/mtls-migration/)
- [Auto mTLS](https://istio.io/latest/docs/tasks/security/authentication/authn-policy/#auto-mutual-tls)
- [Secure Gateways](https://istio.io/latest/docs/tasks/security/gateway-api/)
