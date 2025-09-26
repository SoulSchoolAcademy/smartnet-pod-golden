FROM node:20-bullseye-slim
WORKDIR /app
RUN corepack enable
COPY package*.json ./
RUN npm ci --omit=dev || npm install --production || true
COPY . .
EXPOSE 3101
CMD ["node","index.js"]
