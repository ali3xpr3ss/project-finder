# Сайт для поиска команды

Платформа для поиска команды и участия в проектах. Разработчики, дизайнеры и менеджеры проектов могут находить интересные проекты и формировать команды.

## Технологии

### Бэкенд
- Python 3.9+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic (для миграций)
- Pydantic
- JWT для аутентификации

### Фронтенд
- React
- Material-UI
- Axios
- React Router

## Установка и запуск

### Предварительные требования
- Python 3.9 или выше
- PostgreSQL
- Node.js и npm

### Настройка базы данных
1. Установите PostgreSQL
2. Создайте базу данных:
```sql
CREATE DATABASE site52;
```

### Настройка бэкенда
1. Перейдите в директорию сервера:
```bash
cd server
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/MacOS
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
- Скопируйте `.env.example` в `.env`
- Заполните необходимые переменные окружения

5. Примените миграции:
```bash
alembic upgrade head
```

6. Запустите сервер:
```bash
uvicorn main:app --reload
```

### Настройка фронтенда
1. Перейдите в директорию клиента:
```bash
cd client
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите приложение:
```bash
npm start
```

## API Документация

После запуска сервера, документация API доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Основные функции

1. Аутентификация и авторизация пользователей
2. Создание и управление проектами
3. Поиск проектов по различным критериям
4. Система лайков и подбора команды
5. Уведомления о совпадениях и новых проектах

## Разработка

### Структура проекта
```
.
├── client/              # React фронтенд
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
└── server/              # FastAPI бэкенд
    ├── alembic/        # Миграции
    ├── api/            # API роуты
    ├── core/           # Основные настройки
    ├── models/         # Модели SQLAlchemy
    ├── schemas/        # Схемы Pydantic
    └── services/       # Бизнес-логика
```

## Лицензия

MIT 