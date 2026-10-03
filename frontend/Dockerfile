FROM nginx:alpine

# nginx:alpine already includes an "nginx" user (uid 101) created by
# the upstream image — we reuse it instead of inventing our own.

COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY index.html /usr/share/nginx/html/index.html

ENV BACKEND_HOST=bmi-service
ENV BACKEND_PORT=8000
ENV TRACKER_HOST=tracker-service
ENV TRACKER_PORT=8000
ENV SUMMARY_HOST=summary-worker
ENV SUMMARY_PORT=8000

# Nginx needs write access to these paths at runtime (cache, temp
# files, PID file). Hand ownership to the "nginx" user.
RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid \
                          /var/cache/nginx \
                          /etc/nginx/conf.d

# Switch off root for everything from here on
USER nginx

# Listen on 8080 instead of 80 — ports below 1024 require root
# privileges to bind, which "nginx" (non-root) doesn't have
EXPOSE 8080
