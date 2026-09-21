FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libharfbuzz-subset0 \
    libfontconfig1 \
    libfreetype6 \
    libjpeg62-turbo \
    libopenjp2-7 \
    libffi8 \
    libgdk-pixbuf-2.0-0 \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
