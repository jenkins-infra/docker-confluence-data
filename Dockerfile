FROM nginx:1.21.5-alpine
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./content /usr/share/nginx/html/
