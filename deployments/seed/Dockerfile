FROM python:3.12-slim-trixie

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Keep it dead-simple: no workspace/uv; just a tiny http client.
RUN pip install --no-cache-dir httpx

COPY ./deployments/seed/src /app/src

# Make /app/src importable so `python -m seed` works.
ENV PYTHONPATH="/app/src"

# Sensible defaults (override in compose/env as needed)
ENV API_BASE_URL="http://api:8000/api/v1" \
    POST_COUNT="5" \
    LOOP="false" \
    SLEEP_SECONDS="5"

CMD ["python", "-m", "seed"]
