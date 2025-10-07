FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# добавляем netcat для проверки соединения
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8001

ENTRYPOINT ["./entrypoint.sh"]
