FROM python:3.11.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
&& rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==1.8.5"
RUN pip install "poetry-plugin-export"

COPY pyproject.toml poetry.lock ./

RUN poetry export --format requirements.txt --output requirements.txt --without-hashes --only main

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


FROM python:3.11.12-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH"
ENV APP_ENV=local
ENV PYTHONUNBUFFERED=1

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

COPY . /app

CMD ["python", "app/main.py"]

