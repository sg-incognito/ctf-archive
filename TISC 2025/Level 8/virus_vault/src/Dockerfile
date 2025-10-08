# docker build --platform=linux/amd64 -t virusvault .
# docker run --rm -it -p 8080:80 --name virusvault-1 virusvault
FROM debian:stable-slim

# Install PHP-FPM and nginx
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y ca-certificates apt-transport-https gnupg2 curl lsb-release \
  && curl -fsSL https://packages.sury.org/php/apt.gpg | gpg --dearmor -o /usr/share/keyrings/sury-php.gpg \
  && echo "deb [signed-by=/usr/share/keyrings/sury-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/sury-php.list \
  && apt-get update \
  && apt-get install -y php8.4-fpm php8.4-mbstring php8.4-sqlite3 sqlite3 nginx \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy custom configuration file
COPY nginx.conf /etc/nginx/sites-enabled/default
RUN sed -i 's/;clear_env/clear_env/' /etc/php/8.4/fpm/pool.d/www.conf

# Copy challenge files
RUN mkdir /app && chmod 777 /app
COPY ./app /app

COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port 80
EXPOSE 80

# Start the container by running the startup script
ENV FLAG="TISC{this_is_a_sample_flag}"
CMD ["sh", "/start.sh"]
