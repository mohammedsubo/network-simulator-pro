FROM python:3.11-slim

WORKDIR /app

COPY requirements-production.txt .
RUN pip install --no-cache-dir -r requirements-production.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
