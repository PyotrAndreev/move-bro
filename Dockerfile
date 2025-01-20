# Используем официальный образ Python 3.13.1
FROM python:3.13.1-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .
COPY pyproject.toml .
# Копируем файлы проекта
COPY TelegramBot .
# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt && pip install -e .

#Создаём БД
CMD ["python", "-m", "TelegramBot.data_base"]
# Команда для запуска приложения
CMD ["python", "-m", "TelegramBot.run_bot"]
