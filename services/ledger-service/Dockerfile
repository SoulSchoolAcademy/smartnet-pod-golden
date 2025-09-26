FROM node:20-bullseye-slim
WORKDIR /app
RUN corepack enable

# deps for building then runtime
COPY package*.json ./
RUN npm install || npm ci || true

# copy source & build
COPY . .
RUN npm run build

# run compiled JS
CMD ["node","dist/index.js"]
