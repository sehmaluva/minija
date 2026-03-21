FROM node:20-alpine as build
WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

COPY frontend/package.json /app/
COPY frontend/pnpm-lock.yaml /app/

RUN pnpm install --frozen-lockfile

COPY frontend /app
RUN pnpm run build && pnpm exec next export

# Production nginx image
FROM nginx:stable-alpine
COPY --from=build /app/out /usr/share/nginx/html
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
