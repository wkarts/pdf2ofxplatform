ARG PHP_BASE_IMAGE=php:8.4-fpm-alpine
ARG COMPOSER_BASE_IMAGE=composer:2.8
ARG NGINX_BASE_IMAGE=nginx:1.28-alpine
ARG REDIS_EXTENSION_VERSION=6.3.0

FROM ${COMPOSER_BASE_IMAGE} AS composer-production
WORKDIR /build
COPY apps/web/composer.* ./
RUN composer install \
    --no-dev \
    --no-interaction \
    --no-progress \
    --prefer-dist \
    --optimize-autoloader \
    --no-scripts

FROM ${COMPOSER_BASE_IMAGE} AS composer-development
WORKDIR /build
COPY apps/web/composer.* ./
RUN composer install \
    --no-interaction \
    --no-progress \
    --prefer-dist \
    --optimize-autoloader \
    --no-scripts

FROM ${PHP_BASE_IMAGE} AS php-runtime
ARG REDIS_EXTENSION_VERSION
WORKDIR /var/www/html

RUN apk add --no-cache \
        icu-libs \
        libzip \
        postgresql-libs \
        sqlite-libs \
        su-exec \
    && apk add --no-cache --virtual .build-deps \
        $PHPIZE_DEPS \
        curl \
        icu-dev \
        libzip-dev \
        postgresql-dev \
        sqlite-dev \
    && docker-php-ext-install -j"$(nproc)" \
        bcmath \
        intl \
        opcache \
        pcntl \
        pdo_pgsql \
        pdo_sqlite \
        zip \
    && mkdir -p /tmp/phpredis \
    && curl --fail --location --silent --show-error \
        --retry 6 --retry-delay 5 --retry-all-errors \
        "https://github.com/phpredis/phpredis/archive/refs/tags/${REDIS_EXTENSION_VERSION}.tar.gz" \
        | tar -xz --strip-components=1 -C /tmp/phpredis \
    && cd /tmp/phpredis \
    && phpize \
    && ./configure --enable-redis \
    && make -j"$(nproc)" \
    && make install \
    && docker-php-ext-enable redis \
    && php -r 'if (!extension_loaded("redis")) { fwrite(STDERR, "Extensão redis não carregada.\n"); exit(1); }' \
    && cd / \
    && rm -rf /tmp/phpredis \
    && apk del .build-deps

COPY apps/web/docker/php.ini /usr/local/etc/php/conf.d/99-pdf2ofx.ini
COPY apps/web/docker/www.conf /usr/local/etc/php-fpm.d/zz-pdf2ofx.conf
COPY apps/web/ ./
RUN mkdir -p storage/app storage/framework/cache storage/framework/sessions storage/framework/views storage/logs bootstrap/cache \
    && chown -R www-data:www-data storage bootstrap/cache

COPY apps/web/docker/entrypoint.sh /usr/local/bin/pdf2ofx-entrypoint
RUN chmod +x /usr/local/bin/pdf2ofx-entrypoint

EXPOSE 9000
ENTRYPOINT ["pdf2ofx-entrypoint"]
CMD ["php-fpm", "-F"]

FROM php-runtime AS app
COPY --from=composer-production /build/vendor ./vendor
RUN php artisan package:discover --ansi \
    && chown -R www-data:www-data storage bootstrap/cache

FROM php-runtime AS app-test
COPY --from=composer-development /build/vendor ./vendor
RUN php artisan package:discover --ansi \
    && chown -R www-data:www-data storage bootstrap/cache
CMD ["php", "artisan", "test"]

# O gateway é independente do estágio PHP. Assim, a imagem NGINX não recompila
# extensões PHP e não fica bloqueada por falhas do build da aplicação.
FROM ${NGINX_BASE_IMAGE} AS gateway
COPY apps/web/docker/nginx.conf /etc/nginx/nginx.conf
COPY apps/web/docker/default.conf /etc/nginx/conf.d/default.conf
COPY apps/web/public /var/www/html/public
EXPOSE 8080
