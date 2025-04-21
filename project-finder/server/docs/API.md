# API Documentation

## Аутентификация

### Регистрация
```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "StrongP@ss123",
    "name": "User Name",
    "role": "user",
    "description": "User description",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "experience": "5 years",
    "telegram_username": "@username"
}
```

#### Ответ
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "role": "user",
    "description": "User description",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "experience": "5 years",
    "telegram_username": "@username",
    "is_active": true,
    "created_at": "2024-03-20T12:00:00Z",
    "updated_at": null
}
```

### Вход
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=StrongP@ss123
```

#### Ответ
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

### Обновление токена
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Ответ
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

### Получение информации о текущем пользователе
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

#### Ответ
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "role": "user",
    "description": "User description",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "experience": "5 years",
    "telegram_username": "@username",
    "is_active": true,
    "created_at": "2024-03-20T12:00:00Z",
    "updated_at": null
}
```

## Пользователи

### Получение списка пользователей
```http
GET /api/v1/users?skip=0&limit=10
Authorization: Bearer <access_token>
```

#### Ответ
```json
{
    "items": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "User Name",
            "role": "user",
            "description": "User description",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience": "5 years",
            "telegram_username": "@username",
            "is_active": true,
            "created_at": "2024-03-20T12:00:00Z",
            "updated_at": null
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
}
```

### Получение информации о пользователе
```http
GET /api/v1/users/{user_id}
Authorization: Bearer <access_token>
```

#### Ответ
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "role": "user",
    "description": "User description",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "experience": "5 years",
    "telegram_username": "@username",
    "is_active": true,
    "created_at": "2024-03-20T12:00:00Z",
    "updated_at": null
}
```

### Обновление информации о пользователе
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "New Name",
    "description": "New description",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "experience": "6 years",
    "telegram_username": "@new_username"
}
```

#### Ответ
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "New Name",
    "role": "user",
    "description": "New description",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "experience": "6 years",
    "telegram_username": "@new_username",
    "is_active": true,
    "created_at": "2024-03-20T12:00:00Z",
    "updated_at": "2024-03-20T13:00:00Z"
}
```

## Безопасность

### Токены
- Access Token действителен 24 часа
- Refresh Token действителен 7 дней
- При истечении Access Token используйте Refresh Token для получения нового

### Ограничения
- Максимальное количество попыток входа: 5 в течение 15 минут
- Минимальная длина пароля: 8 символов
- Пароль должен содержать как минимум:
  - 1 заглавную букву
  - 1 строчную букву
  - 1 цифру
  - 1 специальный символ

### Защита от атак
- Защита от SQL-инъекций
- Защита от XSS
- Защита от CSRF
- Rate limiting: 60 запросов в минуту

## Коды ответов

- 200: Успешный запрос
- 201: Успешное создание
- 400: Неверный запрос
  - Неверный формат email
  - Слабый пароль
  - Превышена максимальная длина полей
- 401: Не авторизован
  - Неверный токен
  - Истекший токен
- 403: Доступ запрещен
  - Аккаунт заблокирован
  - Недостаточно прав
- 404: Не найдено
  - Пользователь не найден
  - Ресурс не найден
- 422: Ошибка валидации
  - Неверный формат данных
  - Отсутствуют обязательные поля
- 429: Слишком много запросов
  - Превышен лимит запросов
  - Слишком много попыток входа
- 500: Внутренняя ошибка сервера

## Уведомления

### Получение списка уведомлений
```http
GET /api/v1/notifications?skip=0&limit=10
Authorization: Bearer <access_token>
```

#### Ответ
```json
{
    "items": [
        {
            "id": 1,
            "title": "Новый подходящий проект",
            "message": "Найден проект, соответствующий вашим навыкам",
            "type": "project_match",
            "related_id": 123,
            "is_read": false,
            "created_at": "2024-03-20T12:00:00Z",
            "read_at": null
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
}
```

### Отметка уведомления как прочитанного
```http
POST /api/v1/notifications/{notification_id}/read
Authorization: Bearer <access_token>
```

#### Ответ
```json
{
    "id": 1,
    "title": "Новый подходящий проект",
    "message": "Найден проект, соответствующий вашим навыкам",
    "type": "project_match",
    "related_id": 123,
    "is_read": true,
    "created_at": "2024-03-20T12:00:00Z",
    "read_at": "2024-03-20T12:30:00Z"
}
```

### Отметка всех уведомлений как прочитанных
```http
POST /api/v1/notifications/read-all
Authorization: Bearer <access_token>
```

#### Ответ
```json
{
    "success": true
}
```

## Поиск и кэширование

### Поиск проектов
```http
GET /api/v1/projects/search?query=python&status=active&skip=0&limit=10
Authorization: Bearer <access_token>
```

#### Параметры
- `query`: Текст для семантического поиска
- `status`: Фильтр по статусу проекта
- `technology`: Фильтр по технологиям
- `role`: Фильтр по требуемым ролям
- `skip`: Смещение для пагинации
- `limit`: Количество результатов на странице

#### Ответ
```json
{
    "items": [
        {
            "id": 1,
            "name": "Python Backend Project",
            "description": "Разработка бэкенда на Python",
            "technologies": ["Python", "FastAPI", "PostgreSQL"],
            "required_roles": ["developer"],
            "status": "active",
            "created_at": "2024-03-20T12:00:00Z",
            "updated_at": null
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
}
```

### Поиск профилей
```http
GET /api/v1/profiles/search?query=python&skip=0&limit=10
Authorization: Bearer <access_token>
```

#### Параметры
- `query`: Текст для семантического поиска
- `technology`: Фильтр по технологиям
- `role`: Фильтр по ролям
- `skip`: Смещение для пагинации
- `limit`: Количество результатов на странице

#### Ответ
```json
{
    "items": [
        {
            "id": 1,
            "name": "John Doe",
            "description": "Python Developer",
            "technologies": ["Python", "FastAPI", "PostgreSQL"],
            "roles": ["developer"],
            "experience": "5 years",
            "created_at": "2024-03-20T12:00:00Z",
            "updated_at": null
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
}
```

## Кэширование

Все результаты поиска автоматически кэшируются в Redis для улучшения производительности. Кэш обновляется при:
- Создании нового проекта
- Обновлении проекта
- Создании нового профиля
- Обновлении профиля

Время жизни кэша: 1 час 