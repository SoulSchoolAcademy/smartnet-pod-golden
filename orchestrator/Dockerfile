FROM node:20-alpine
WORKDIR /app
RUN corepack enable
COPY package.json ./
RUN pnpm install --frozen-lockfile || pnpm install
COPY tsconfig.json ./
COPY src ./src
RUN pnpm build
EXPOSE 8765
CMD ["pnpm","start"]
