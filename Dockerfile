FROM nginx:1.28.0-alpine
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./content /usr/share/nginx/html/
