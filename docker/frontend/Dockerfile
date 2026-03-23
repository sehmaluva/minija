FROM node:20-alpine as build
WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

COPY frontend/package.json /app/
COPY frontend/pnpm-lock.yaml /app/

RUN pnpm install --frozen-lockfile

COPY frontend /app
RUN pnpm run build

# Production Next.js server image
FROM node:20-alpine as prod
WORKDIR /app
COPY --from=build /app .
EXPOSE 3000
CMD ["npm", "start"]
