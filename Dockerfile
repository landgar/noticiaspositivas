FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron git openssh-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .
COPY src ./src
COPY config ./config
COPY plantillas ./plantillas
COPY content ./content
COPY layouts ./layouts
COPY hugo.toml ./hugo.toml
COPY main.py .
COPY .env.example .env

RUN python -m pip install --upgrade pip && python -m pip install -e .

CMD ["python", "main.py"]
