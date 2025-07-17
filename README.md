# Transcribe.Cafe Backend

Отдельный backend сервис для Transcribe.Cafe, готовый к деплою на Railway.

## Функциональность

- **FastAPI** REST API для управления видео и заданиями
- **SQLAlchemy** ORM с поддержкой SQLite (локально) и PostgreSQL (продакшн)
- **Alembic** миграции схемы базы данных
- **Worker API** для интеграции с локальным воркером
- **CORS** поддержка для фронтенда

## Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env под ваши потребности
```

### 3. Инициализация базы данных

```bash
# Применить миграции
alembic upgrade head

# Мигрировать данные из JSON (если есть)
python migrate_data.py ../worker/database.json
```

### 4. Запуск сервера

```bash
# Разработка
uvicorn app.main:app --reload

# Продакшн
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Публичные endpoints (для фронтенда)

- `GET /health` - проверка здоровья сервиса
- `GET /api/videos` - список всех видео
- `GET /api/videos/{id}` - получить конкретное видео
- `POST /api/videos` - добавить новое видео для обработки
- `POST /api/videos/{id}/rating` - установить рейтинг видео
- `POST /api/videos/{id}/insights` - запросить генерацию insights

### Worker endpoints (для локального воркера)

- `GET /api/worker/jobs` - получить задания для обработки
- `POST /api/worker/jobs/{id}/claim` - забрать задание в работу
- `POST /api/worker/jobs/{id}/result` - отправить результат обработки
- `POST /api/worker/jobs/{id}/progress` - обновить прогресс

## Конфигурация

### Переменные окружения (.env)

```bash
# База данных
DATABASE_URL=sqlite:///./app.db  # Локально
# DATABASE_URL=postgresql://user:pass@host:port/db  # Railway

# API настройки
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS (фронтенд)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Интеграция с воркером
WORKER_API_KEY=your-secure-key-here
```

### База данных

**Локальная разработка (SQLite):**
```bash
DATABASE_URL=sqlite:///./app.db
```

**Продакшн (PostgreSQL):**
```bash
# Установить psycopg2-binary
pip install psycopg2-binary

# Railway автоматически предоставляет DATABASE_URL
DATABASE_URL=postgresql://user:pass@host:port/db
```

## Миграции

### Создание новой миграции

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Откат миграции

```bash
alembic downgrade -1  # На одну назад
alembic downgrade base  # К началу
```

## Интеграция с воркером

Backend предоставляет API для взаимодействия с локальным воркером:

1. **Воркер опрашивает** `/api/worker/jobs` для получения новых заданий
2. **Воркер забирает** задание через `/api/worker/jobs/{id}/claim`
3. **Воркер отправляет** результат через `/api/worker/jobs/{id}/result`

### Аутентификация воркера

Воркер должен отправлять header:
```
X-Worker-Token: your-worker-api-key
```

## Деплой на Railway

### 1. Подготовка

```bash
# Добавить PostgreSQL зависимость
echo "psycopg2-binary>=2.9.0" >> requirements.txt

# Создать start.sh
echo "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > start.sh
chmod +x start.sh
```

### 2. Railway деплой

```bash
# Установить Railway CLI
npm install -g @railway/cli

# Логин и деплой
railway login
railway init
railway up
```

### 3. Настройка на Railway

- **PostgreSQL**: добавить через Railway Dashboard
- **Environment Variables**: Railway автоматически установит `DATABASE_URL`
- **Custom Variables**: установить `WORKER_API_KEY`, `ALLOWED_ORIGINS`

## Тестирование

```bash
# Быстрый тест API
python test_api.py

# Запуск тестов (если есть)
pytest tests/

# Тест подключения к базе
python -c "from app.database import engine; print('DB OK')"
```

## Структура проекта

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI приложение
│   ├── config.py        # Конфигурация
│   ├── database.py      # Подключение к БД
│   ├── schemas.py       # Pydantic схемы
│   ├── models/          # SQLAlchemy модели
│   │   ├── video.py
│   │   └── job.py
│   └── api/             # API роуты
│       ├── videos.py
│       └── worker.py
├── alembic/             # SQL миграции
├── requirements.txt
├── migrate_data.py      # Миграция из JSON
├── test_api.py         # Тестирование API
└── README.md
```

## Совместимость

Backend полностью совместим с существующим фронтендом - все API endpoints сохраняют тот же формат ответов, что и `unified_app.py`.

## Мониторинг

- **Health check**: `GET /health`
- **Logs**: FastAPI автоматически логирует запросы
- **Metrics**: можно добавить Prometheus метрики при необходимости