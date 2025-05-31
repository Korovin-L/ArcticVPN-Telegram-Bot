# Используем минимальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию в контейнере
WORKDIR /bot

# Копируем файлы проекта
COPY bot/requirements.txt ./
COPY bot/run.py ./ 
COPY bot/config.py ./
COPY bot/app ./app


# Устанавливаем зависимости
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


CMD ["python", "run.py"]
