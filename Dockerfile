# Используем официальный образ Python 3.13.1
FROM python:3.13.1-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

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
