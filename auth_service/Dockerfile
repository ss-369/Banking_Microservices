FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY auth_service/ ./auth_service/
COPY utils.py .

EXPOSE 8001

CMD ["python", "-m", "auth_service.auth_service"]