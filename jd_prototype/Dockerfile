# JD Generator — Flask + MySQL
# Local MySQL is configured via .env; this image does not require Docker MySQL.
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

RUN mkdir -p uploads/resumes

EXPOSE 6001

# Application entrypoint (unchanged). MySQL host/credentials come from env.
CMD ["python", "app.py"]
