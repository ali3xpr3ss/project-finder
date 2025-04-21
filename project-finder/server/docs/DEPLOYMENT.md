# Инструкции по развертыванию

## Требования

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Node.js 18+ (для клиентской части)

## Настройка окружения

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/site52.git
cd site52
```

2. Создайте виртуальное окружение Python:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
.\venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # для разработки
```

4. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

5. Настройте переменные окружения в .env:
```env
DATABASE_URL=postgresql://user:password@localhost/site52
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
JWT_SECRET=your_secure_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
API_V1_STR=/api/v1
PROJECT_NAME=Site52
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## Настройка Redis

1. Установите Redis:
```bash
# На macOS
brew install redis
brew services start redis

# На Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis-server
```

2. Проверьте работу Redis:
```bash
redis-cli ping
# Должен ответить: PONG
```

## Настройка базы данных

1. Создайте базу данных PostgreSQL:
```bash
createdb site52
```

2. Примените миграции:
```bash
alembic upgrade head
```

## Запуск сервера

1. Запустите сервер в режиме разработки:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Для продакшена используйте gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Настройка клиентской части

1. Перейдите в директорию клиента:
```bash
cd client
```

2. Установите зависимости:
```bash
npm install
```

3. Создайте файл .env:
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

4. Запустите клиент в режиме разработки:
```bash
npm start
```

5. Для продакшена соберите приложение:
```bash
npm run build
```

## Развертывание на сервере

1. Настройте Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/client/build;
        try_files $uri $uri/ /index.html;
    }
}
```

2. Настройте SSL с помощью Let's Encrypt:
```bash
sudo certbot --nginx -d your-domain.com
```

3. Настройте systemd для автоматического запуска:
```ini
[Unit]
Description=Site52 API
After=network.target redis.service

[Service]
User=your-user
Group=your-group
WorkingDirectory=/path/to/server
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

## Мониторинг

1. Настройте логирование:
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

2. Настройте мониторинг с помощью Prometheus и Grafana:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'site52'
    static_configs:
      - targets: ['localhost:8000']
```

## Резервное копирование

1. Настройте автоматическое резервное копирование базы данных и Redis:
```bash
#!/bin/bash
# Резервное копирование PostgreSQL
pg_dump -U your-user site52 > backup_db_$(date +%Y%m%d).sql

# Резервное копирование Redis
redis-cli SAVE
cp /var/lib/redis/dump.rdb backup_redis_$(date +%Y%m%d).rdb
```

2. Добавьте скрипт в crontab:
```bash
0 0 * * * /path/to/backup.sh
```

## Обновление

1. Остановите сервис:
```bash
sudo systemctl stop site52
```

2. Обновите код:
```bash
git pull
```

3. Примените миграции:
```bash
alembic upgrade head
```

4. Перезапустите сервис:
```bash
sudo systemctl restart site52
``` 