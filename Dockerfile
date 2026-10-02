FROM python:3.12-slim

# Не создавать .pyc и сразу выводить логи в консоль
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1. Устанавливаем Poetry
RUN pip install --upgrade pip "poetry==1.8.5"

# 2. ВАЖНО: отключаем создание виртуального окружения внутри Docker-образа.
#    Зависимости ставятся прямо в системный Python контейнера.
RUN poetry config virtualenvs.create false

# 3. Сначала копируем только файлы зависимостей (для кеширования слоёв)
COPY pyproject.toml poetry.lock ./

# 4. Устанавливаем зависимости через Poetry (сам проект как пакет не ставим)
RUN poetry install --no-root --no-interaction --no-ansi

# 5. Копируем код Django-проекта (папка с manage.py)
COPY mysite .

EXPOSE 8000

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
