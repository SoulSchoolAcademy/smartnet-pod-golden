# services/ledger-service/Dockerfile
FROM node:20-bookworm-slim

WORKDIR /app
RUN corepack enable

# deps
COPY package.json ./
COPY pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install

# build
COPY tsconfig.json ./
COPY src ./src
RUN pnpm build

# expose only if ledger has an HTTP port; otherwise you can remove this
# EXPOSE 3102

CMD ["node","--enable-source-maps","dist/index.js"]
