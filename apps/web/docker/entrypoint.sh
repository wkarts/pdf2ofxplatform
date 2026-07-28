#!/bin/sh
set -eu

mkdir -p \
  storage/app \
  storage/framework/cache \
  storage/framework/sessions \
  storage/framework/views \
  storage/logs \
  bootstrap/cache

chown -R www-data:www-data storage bootstrap/cache

case "${1:-}" in
  php-fpm|php-fpm*)
    exec "$@"
    ;;
  *)
    exec su-exec www-data "$@"
    ;;
esac
