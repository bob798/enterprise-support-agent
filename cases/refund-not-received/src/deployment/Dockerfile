FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy case source code
COPY cases/refund-not-received/solution/src/ ./src/

EXPOSE 8000

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
