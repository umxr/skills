FROM node:20-alpine
WORKDIR /app
COPY . .
RUN corepack enable && pnpm install --frozen-lockfile && pnpm --filter @harbor/api build
EXPOSE 4000
CMD ["node", "apps/api/dist/server.js"]
