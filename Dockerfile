# 22PM Frontend — Static Web App Dockerfile
# Build: docker build -f 22pm-business/Dockerfile -t 22pm-frontend .
# Run:   docker run -p 80:80 22pm-frontend

FROM nginx:alpine

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy frontend assets
# Note: We copy everything from 22pm-business/ into nginx html root.
# The logo file lives one directory above, so we copy it too.
COPY 22pmlogo24.png /usr/share/nginx/html/22pmlogo24.png
COPY 22pm-business/ ./

# Optional: Add custom nginx config (SPA fallback, caching headers)
# Uncomment if you want custom config:
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1