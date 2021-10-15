FROM nginx:latest
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./content /usr/share/nginx/html/
