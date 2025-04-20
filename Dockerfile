FROM python:3.12

WORKDIR /code

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

COPY poetry.lock pyproject.toml ./
COPY migrations ./migrations
COPY src/ticket_api ./src/ticket_api
COPY alembic.ini ./
COPY README.md ./

RUN poetry install

EXPOSE 8000

CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run ticket-api run prod"]
