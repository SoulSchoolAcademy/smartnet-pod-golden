# SmartNET Golden Dev Pod
# Base: Ubuntu 22.04 + Node 20 LTS + pnpm 9 + code-server 4.93.1
FROM ubuntu:22.04

ARG NODE_VERSION=20.16.0
ARG PNPM_VERSION=9.12.3
ARG CS_VER=4.93.1

ENV DEBIAN_FRONTEND=noninteractive         LANG=C.UTF-8         LC_ALL=C.UTF-8         SHELL=/bin/bash

# Core utilities
RUN apt-get update && apt-get install -y --no-install-recommends \ 
    curl ca-certificates git unzip xz-utils nano openssh-client locales tini         && rm -rf /var/lib/apt/lists/*         && locale-gen en_US.UTF-8

# Install Node (official tarball)
RUN mkdir -p /usr/local/node \ 
    && curl -fsSL https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz            | tar -xJ -C /usr/local/node --strip-components=1

ENV PATH="/usr/local/node/bin:${PATH}"

# Enable corepack & pin pnpm
RUN corepack enable && corepack prepare "pnpm@${PNPM_VERSION}" --activate

# Install code-server
RUN mkdir -p /opt/code-server && cd /opt \ 
    && curl -fsSL -o cs.tgz "https://github.com/coder/code-server/releases/download/v${CS_VER}/code-server-${CS_VER}-linux-amd64.tar.gz"         && tar -xzf cs.tgz && rm cs.tgz         && mv code-server-${CS_VER}-linux-amd64 /opt/code-server

# Create non-root user and workspace
RUN useradd -ms /bin/bash naya && mkdir -p /workspace && chown -R naya:naya /workspace /opt/code-server
USER naya
WORKDIR /workspace

COPY --chown=naya:naya scripts/start.sh /opt/scripts/start.sh
COPY --chown=naya:naya scripts/doctor.sh /usr/local/bin/smnet-doctor
COPY --chown=naya:naya scripts/new-next.sh /usr/local/bin/new-next
RUN chmod +x /opt/scripts/start.sh /usr/local/bin/smnet-doctor /usr/local/bin/new-next

ENV CODE_SERVER_PASSWORD=SmartNet!2025         CS_PORT=8080         WORKSPACE_DIR=/workspace

EXPOSE 8080 3000 5173

ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["/opt/scripts/start.sh"]
