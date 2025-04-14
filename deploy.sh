#!/bin/bash

set -e

echo "Starting deployment..."

# Остановка старых контейнеров
docker-compose down

# Сборка новых образов
docker-compose build

# Запуск сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

echo "Deployment completed!" 