FROM python:3.9-slim AS requirements-stage
WORKDIR /tmp
# Instalar dependencias del sistema necesarias para Poetry
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
# Instalar Poetry
RUN pip install poetry poetry-plugin-export
COPY ./src/pyproject.toml ./src/poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
ENV C_FORCE_ROOT=1
# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    git \
    gettext \
    libffi-dev \
    gcc \
    figlet \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install psycopg2-binary
COPY ./src/. /code