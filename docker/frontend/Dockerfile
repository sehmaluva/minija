FROM node:20-alpine as build
WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

COPY frontend/frontend/package.json /app/
COPY frontend/frontend/pnpm-lock.yaml /app/
COPY frontend/frontend/.npmrc /app/ 2>/dev/null || true

RUN pnpm install --frozen-lockfile

COPY frontend/frontend /app
RUN pnpm run build

# Production nginx image
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
