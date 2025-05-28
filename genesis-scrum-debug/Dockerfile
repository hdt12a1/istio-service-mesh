# Image: harbor.tcbs.com.vn/infra/java-apm:21.0.6_7-alpine-apm1.53.0
# Base Java image with Elastic APM Agent v1.53.0 pre-installed with grpcurl for debugging

# Stage 1: Install grpcurl using Go for Alpine compatibility
FROM golang:alpine as grpcurl-installer

WORKDIR /go

# Install git and build dependencies
RUN apk add --no-cache git

# Install grpcurl using go install
RUN go install github.com/fullstorydev/grpcurl/cmd/grpcurl@v1.9.3

# Verify the installation
RUN ls -la /go/bin/grpcurl

# Stage 2: Final image
FROM harbor.tcbs.com.vn/infra/java/eclipse-temurin:21.0.6_7-jre-alpine

# Set up environment
USER root
ENV TZ=Asia/Ho_Chi_Minh
ENV JDK_JAVA_OPTIONS="--add-modules java.se --add-exports java.base/jdk.internal.ref=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/sun.nio.ch=ALL-UNNAMED --add-opens java.management/sun.management=ALL-UNNAMED --add-opens jdk.management/com.sun.management.internal=ALL-UNNAMED"
WORKDIR /opt/tcbs

# Install necessary tools
RUN apk add --no-cache curl tar unzip

# Download Elastic APM Agent v1.53.0 directly from Maven Central
RUN curl -L https://repo1.maven.org/maven2/co/elastic/apm/elastic-apm-agent/1.53.0/elastic-apm-agent-1.53.0.jar \
     -o /opt/tcbs/elastic-apm-agent.jar && \
    chmod 644 /opt/tcbs/elastic-apm-agent.jar

# Copy grpcurl from the installer stage
COPY --from=grpcurl-installer /go/bin/grpcurl /usr/local/bin/
RUN chmod +x /usr/local/bin/grpcurl

# Verify grpcurl installation
RUN grpcurl --version

# Set up a directory for your application
WORKDIR /opt/tcbs

# This is where you would typically add your application files
# COPY --from=your-build-stage /path/to/your/app /opt/tcbs/

# Example entrypoint with APM agent enabled
ENTRYPOINT ["java", "-javaagent:/opt/tcbs/elastic-apm-agent.jar", "org.springframework.boot.loader.JarLauncher"]
 