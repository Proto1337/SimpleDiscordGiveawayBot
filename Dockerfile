FROM python:alpine

WORKDIR /app

# appuser - NEVER EVER ROOT
RUN adduser -D appuser
USER appuser

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser . .

CMD ["python", "main.py"]
