FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir Pillow fastapi uvicorn psycopg2-binary requests httpx pytumblr coincurve websocket-client

# Copy service
COPY main.py .

# auto-publisher adapters are mounted as volume
EXPOSE 8085

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085"]
