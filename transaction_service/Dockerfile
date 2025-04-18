FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY transaction_service/ ./transaction_service/
COPY utils.py .

EXPOSE 8003

CMD ["python", "-m", "transaction_service.transaction_service"]