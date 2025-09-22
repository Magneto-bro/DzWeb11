FROM python:3.12-slim

WORKDIR /app

# копіюємо файли з залежностями
COPY pyproject.toml poetry.lock* /app/

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --without dev --no-interaction --no-ansi

# копіюємо весь код
COPY ./src /app/src

CMD ["uvicorn", "contacts_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
