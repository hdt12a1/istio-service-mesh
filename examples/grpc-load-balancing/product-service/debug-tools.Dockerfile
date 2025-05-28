FROM alpine:3.18

# Install curl, bash, and other useful tools
RUN apk add --no-cache \
    curl \
    bash \
    jq \
    ca-certificates \
    wget \
    netcat-openbsd \
    bind-tools \
    openssl \
    git

# Install grpcurl
RUN wget -O /tmp/grpcurl.tar.gz https://github.com/fullstorydev/grpcurl/releases/download/v1.8.7/grpcurl_1.8.7_linux_x86_64.tar.gz && \
    tar -xzf /tmp/grpcurl.tar.gz -C /usr/local/bin && \
    rm /tmp/grpcurl.tar.gz && \
    chmod +x /usr/local/bin/grpcurl

# Add a script to help with testing
RUN echo '#!/bin/bash\necho "Debug Tools Container"\necho "Available tools: curl, grpcurl, jq, netcat, dig, openssl"\necho "Example gRPC command: grpcurl -d '\''{"product_id": "p1"}'\'' product-service.avenger.svc.cluster.local:50051 product.ProductService/GetProduct"\necho "Example curl command: curl -v http://product-service.avenger.svc.cluster.local:8080/health"\n/bin/bash\n' > /usr/local/bin/help.sh && \
    chmod +x /usr/local/bin/help.sh

WORKDIR /app

# Set the entrypoint to keep the container running
ENTRYPOINT ["sleep", "infinity"]
