# ---------------------------------------------------------------------------
# The Forge — Frontend Dockerfile
# Multi-stage: build with Node, serve with nginx
#
# Build context must be the MONOREPO ROOT (not frontend/) so that the
# @constants alias (../backend/src/constants) resolves during tsc + vite build.
# ---------------------------------------------------------------------------

# --- Stage 1: Build ----------------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app/frontend

# Copy package files first for better layer caching
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --prefer-offline

# Copy frontend source
COPY frontend/ .

# Copy shared backend constants that the frontend imports via @constants alias
COPY backend/src/constants/ /app/backend/src/constants/

# The VERSION file is in the monorepo root
ARG APP_VERSION=0.0.0
RUN echo "${APP_VERSION}" > /app/VERSION

# Build-time env vars (baked into the bundle)
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# --- Stage 2: Serve with nginx -----------------------------------------------
FROM nginx:1.27-alpine AS production

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from build stage
COPY --from=build /app/frontend/dist /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
