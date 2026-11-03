FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY frontend ./frontend
COPY evaluation ./evaluation
COPY sample_data ./sample_data
COPY docs ./docs
COPY .env.example .
COPY README.md .

RUN mkdir -p /app/data/uploads /app/data/chroma

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
