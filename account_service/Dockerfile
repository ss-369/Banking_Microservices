FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY account_service/ ./account_service/
COPY utils.py .

EXPOSE 8002

CMD ["python", "-m", "account_service.account_service"]