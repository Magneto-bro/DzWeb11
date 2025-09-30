FROM python:3.12-slim

WORKDIR /app


COPY pyproject.toml poetry.lock* /app/

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --without dev --no-interaction --no-ansi


COPY ./src /app/src

CMD ["uvicorn", "src.contacts_api.main:app", "--host", "0.0.0.0", "--port", "8000"]


