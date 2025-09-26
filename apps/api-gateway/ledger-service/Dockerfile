# services/ledger-service/Dockerfile
FROM node:20-bookworm-slim
WORKDIR /app
RUN corepack enable

# deps
COPY package.json ./
RUN pnpm install --frozen-lockfile || pnpm install

# build
COPY tsconfig.json ./
COPY src ./src
RUN pnpm build

CMD ["node","--enable-source-maps","dist/index.js"]
