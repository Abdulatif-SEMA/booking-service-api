# Booking Service API

REST API системы бронирования номеров на FastAPI: регистрация, JWT-авторизация, роли Admin/Client, каталог номеров с фильтрами и бронирование с защитой от пересечения дат.

## Стек

- Python, FastAPI, Uvicorn
- PostgreSQL, SQLAlchemy 2.0
- JWT (PyJWT), хэширование паролей через bcrypt
- pytest

## Возможности

- Регистрация и вход (`/api/auth/register`, `/api/auth/login`)
- Роли: `admin` (управляет номерами) и `client` (создаёт брони)
- Просмотр номеров с фильтрами по цене, количеству гостей и свободным датам
- Бронирование с проверкой, что даты не пересекаются с другими бронями
- Просмотр своих активных броней

## Эндпоинты

| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| POST | `/api/auth/register` | все | Регистрация |
| POST | `/api/auth/login` | все | Вход, возвращает JWT |
| GET | `/api/rooms` | все | Список номеров (`min_price`, `max_price`, `guests`, `check_in`, `check_out`) |
| POST | `/api/rooms` | admin | Добавить номер |
| POST | `/api/bookings` | авторизованные | Создать бронь |
| GET | `/api/bookings/my` | авторизованные | Мои активные брони |

Интерактивная документация (Swagger): `http://127.0.0.1:8000/docs`

## Запуск

1. Клонировать репозиторий и создать окружение:
   ```bash
   git clone https://github.com/Abdulatif-SEMA/booking-service-api.git
   cd booking-service-api
   python -m venv venv
   venv\Scripts\activate        # Linux/Mac: source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Создать базу PostgreSQL `booking`.
3. Скопировать `.env.example` в `.env` и указать свой пароль и секретный ключ.
4. Запустить сервер:
   ```bash
   uvicorn app.main:app --reload
   ```

Таблицы создаются автоматически при первом запуске.

## Как получить роль admin

Все новые пользователи регистрируются как `client`. Чтобы назначить администратора:
```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

## Тесты

Тесты используют временную SQLite-базу, основную базу они не затрагивают:
```bash
python -m pytest -v
```

Проверяются регистрация, дубликат email, неверный пароль, запрет создания номеров клиентом и логика бронирования (пересечение дат, заезд в день выезда).

## Структура проекта

```
app/
├── main.py        # точка входа
├── config.py      # настройки из .env
├── database.py    # подключение к БД
├── models.py      # User, Room, Booking
├── schemas.py     # схемы запросов и ответов
├── security.py    # хэши паролей и JWT
├── deps.py        # зависимости: БД, текущий пользователь, проверка роли
└── routers/       # auth, rooms, bookings
tests/
```