#!/bin/bash

nginx -g 'daemon off;' &
/usr/sbin/php-fpm8.4 &

wait
