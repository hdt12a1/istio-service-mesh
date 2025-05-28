# 1st-stage: compile & build
FROM harbor.tcbs.com.vn/infra/maven:3.9-eclipse-temurin-21-jammy-v2 AS builder

# Additional Maven build options
ARG MAVEN_ADDITIONAL_OPTS
ARG JAR_PATH=target/*.jar
USER root
WORKDIR /opt/tcbs

COPY settings.xml /root/.m2/settings.xml
COPY . .

RUN --mount=type=cache,uid=1000,gid=1000,target=/home/tcbs/.m2/repository \
    mvn -U -B ${MAVEN_ADDITIONAL_OPTS} clean package

FROM harbor.tcbs.com.vn/base/eclipse-temurin:21-jre-jammy as extract

WORKDIR /opt/tcbs

ARG JAR_PATH=target/*.jar

COPY --from=builder /opt/tcbs/${JAR_PATH} ./application.jar

# Intermediate stage for installing grpcurl
FROM alpine:3.19 as grpcurl-installer

WORKDIR /tmp

# Install grpcurl for gRPC debugging - direct binary download approach
RUN apk add --no-cache curl

# Download pre-built binary directly
RUN GRPCURL_VERSION="1.9.3" && \
    mkdir -p /tmp/bin && \
    cd /tmp/bin && \
    curl -L -o grpcurl "https://github.com/fullstorydev/grpcurl/releases/download/v${GRPCURL_VERSION}/grpcurl_${GRPCURL_VERSION}_linux_x86_64" && \
    chmod +x grpcurl

# Copy grpcurl from the installer stage
FROM harbor.tcbs.com.vn/base/eclipse-temurin:21-jre-jammy as extract
WORKDIR /opt/tcbs
COPY --from=builder /opt/tcbs/${JAR_PATH} ./application.jar
COPY --from=grpcurl-installer /tmp/bin/grpcurl /usr/local/bin/
RUN chmod +x /usr/local/bin/grpcurl
RUN java -Djarmode=layertools -jar application.jar extract

# 2nd-stage: package - Using the pre-built image with APM agent
# This base image already contains Elastic APM Agent v1.53.0 at /opt/tcbs/elastic-apm-agent.jar
# The agent is automatically activated via the -javaagent parameter in the ENTRYPOINT
FROM harbor.tcbs.com.vn/infra/java/eclipse-temurin:21.0.6_7-jre-alpine-apm1.53.0
USER root
ENV JDK_JAVA_OPTIONS="--add-modules java.se --add-exports java.base/jdk.internal.ref=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/sun.nio.ch=ALL-UNNAMED --add-opens java.management/sun.management=ALL-UNNAMED --add-opens jdk.management/com.sun.management.internal=ALL-UNNAMED"
ARG JAR_PATH=target/*.jar
WORKDIR /opt/tcbs

COPY --from=extract /opt/tcbs/dependencies/ ./
COPY --from=extract /opt/tcbs/spring-boot-loader/ ./
COPY --from=extract /opt/tcbs/snapshot-dependencies/ ./
COPY --from=extract /opt/tcbs/application/ ./

ENTRYPOINT ["java", "-javaagent:elastic-apm-agent.jar", "org.springframework.boot.loader.launch.JarLauncher"]