FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
