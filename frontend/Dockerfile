# ---------------------------------------------------------------------------
# The Forge — Frontend Dockerfile
# Multi-stage: build with Node, serve with nginx
# ---------------------------------------------------------------------------

# --- Stage 1: Build ----------------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline

# Copy source and build
COPY . .

# The VERSION file is in the monorepo root — copy it so vite.config.ts can read it
ARG APP_VERSION=0.0.0
RUN echo "${APP_VERSION}" > ../VERSION

# Build-time env vars (baked into the bundle)
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# --- Stage 2: Serve with nginx -----------------------------------------------
FROM nginx:1.27-alpine AS production

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
