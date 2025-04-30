# Используем официальный образ Python 3.13.1
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .
COPY pyproject.toml .
# Копируем файлы проекта
COPY TelegramBot ./TelegramBot
# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt && pip install -e .
COPY run_bot.sh .
#Создаём БД
CMD ["sh", "run_bot.sh"]
