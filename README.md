# 🚀 Mailing Manager

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/docs/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Выгрузка записей из таблицы**

[Установка](#-установка) • [Использование](#-использование)

</div>

---

## 📋 Описание

**Mailing Manager** — это сервис для обработки эксель таблиц.

### ✨ Основные возможности

| Функция | Описание |
|---------|----------|
| 🎫 **Чтение** | Читает таблицу построчно и выгружает записи |
| ✅ **Валидация** | Проверка на дубликаты, пустые строки и тд |
| 🎯 **Применение** | Запускается через managment commands |
| 🧪 **Тестирование** | Покрытие pytest для надежности |

---

---

## 🚀 Быстрый старт

### Требования

- **Python** 3.10+
- **Celery**
- **Redis**
- **uv** (рекомендуется) или pip

### Установка

#### 1. Клонирование репозитория

```bash
git clone https://github.com/sixscale/test-jet-land-promocode.git
cd mailing-service
```
#### 2. Настройка окружения
```bash
cp .env.example .env
```
# Отредактируйте .env при необходимости
#### 3. Установка зависимостей

С использованием uv (рекомендуется ⚡):
```bash
uv sync
```
Или с pip:
```bash
pip install -e .
```

## 💻 Использование
#### Локальный запуск команды
### Необходимо поднять воркер Celery
```bash
uv run celery -A config worker -l info
```
### Далее необходимо поднять Redis
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```
### Далее можно приступать к запуску самой команды
#### запуск необходимо совершать в корневой директории
#### таблица с примерами уже доступна в проекте и заполнена данными
```bash
uv run python manage.py import_mailings apps/mailings/management/commands/test_mailings.xlsx
```
##### * можно так же запустить данную команду с флагом --dry-run 
##### это необходимо для того, чтобы проверить валидность файла без загрузки записей в базу и отправки сообщений
### Запуск тестов
```bash
uv run pytest -v
```
## 🔧 Переменные окружения
## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DEBUG` | Режим отладки | `False` |
| `SECRET_KEY` | Секретный ключ Django | — |
| `DATABASE_URL` | URL подключения к БД | `sqlite:///db.sqlite3` |

Распространяется под лицензией MIT. См. LICENSE для подробностей.
<div align="center">
</div>
