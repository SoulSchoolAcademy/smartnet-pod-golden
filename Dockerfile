# ✅ Do NOT force a platform here (no "--platform=linux/amd64")
FROM ubuntu:22.04

# optional but helpful for cross-arch:
ARG TARGETOS
ARG TARGETARCH
ENV TARGETOS=$TARGETOS TARGETARCH=$TARGETARCH

# if you install arch-specific binaries, pick by $TARGETARCH when needed
# RUN curl -L "https://example.com/tool-${TARGETARCH}" -o /usr/local/bin/tool && chmod +x /usr/local/bin/tool
