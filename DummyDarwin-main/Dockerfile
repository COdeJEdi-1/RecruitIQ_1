# Darwinbox / AI Recruitment Portal — Flask + MySQL
# Local MySQL is optional via .env; default Phase 2 runtime remains SQLite.
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads/resumes static/uploads/jd static/uploads/candidates

EXPOSE 6002

CMD ["python", "app.py"]
