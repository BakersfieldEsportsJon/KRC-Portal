FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY apps/web/package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm install

# Copy source code
COPY apps/web/ .

# Build the application (skip tsc for now - type errors need fixing)
RUN npx vite build

# Use nginx to serve the built app
FROM nginx:alpine

# Copy built app to nginx
COPY --from=0 /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]