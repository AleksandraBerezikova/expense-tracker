# Трекер расходов

RESTful-сервис для учёта личных расходов.

## Стек

- **Бэкенд:** FastAPI 0.115, SQLAlchemy 2 (async), PostgreSQL 15
- **Фронтенд:** Vanilla HTML + CSS + JS, в разработке отдаётся через nginx
- **Тесты:** pytest (бэкенд, 17 тестов) + Jest (фронтенд, 15 тестов)
- **CI:** GitHub Actions - две стадии: test и build

## Локальный запуск

Требования: Docker и Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

- API: <http://localhost:8000> (Swagger UI на <http://localhost:8000/docs>)
- Веб-клиент: <http://localhost:8080>
- PostgreSQL: localhost:5432 (пользователь `expense_user`, база `expenses_db`)

## API

| Метод  | Путь             | Описание                          |
| ------ | ---------------- | --------------------------------- |
| POST   | `/expenses`      | Создать запись о расходе          |
| GET    | `/expenses`      | Список расходов (фильтры: `category`, `date_from`, `date_to`, `skip`, `limit`) |
| PUT    | `/expenses/{id}` | Обновить запись (частичное обновление разрешено) |
| DELETE | `/expenses/{id}` | Удалить запись                    |
| GET    | `/health`        | Проверка работоспособности (пинг БД) |

Полная спецификация - в [проектной документации](docs/project-design.pdf).

## Тесты

Бэкенд (из директории `backend/`):
```bash
pip install -r requirements-dev.txt
pytest -v
```

Фронтенд (из директории `frontend/`):
```bash
npm install
npm test
```

## CI

`.github/workflows/ci.yml` запускается при каждом push в `main` и на pull request'ах:

1. **Стадия test** - `pytest` и `jest` выполняются параллельно в отдельных job'ах.
2. **Стадия build** - сборка Docker-образа (запускается только при успешном прохождении тестов).