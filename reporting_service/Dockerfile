FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY reporting_service/ ./reporting_service/
COPY utils.py .

EXPOSE 8004

CMD ["python", "-m", "reporting_service.reporting_service"]