FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
COPY requirements.txt constraints-verified.txt ./
RUN python -m pip install --no-cache-dir -c constraints-verified.txt --upgrade pip \
    && python -m pip install --no-cache-dir -c constraints-verified.txt -r requirements.txt
COPY fraud_detector/ ./fraud_detector/
COPY web/ ./web/
COPY data/.gitkeep ./data/.gitkeep
RUN useradd --create-home --uid 10001 app && chown -R app:app /app/data
USER app
EXPOSE 8000
CMD ["uvicorn", "fraud_detector.api:app", "--host", "0.0.0.0", "--port", "8000"]
