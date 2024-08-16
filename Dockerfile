FROM nginx:1.26.2-alpine
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./content /usr/share/nginx/html/
