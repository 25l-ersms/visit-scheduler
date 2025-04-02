ARG PYTHON_VERSION=3.13

FROM python:$PYTHON_VERSION AS builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

ARG POETRY_VERSION=2.1.2

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH
RUN poetry self update $POETRY_VERSION

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev

COPY visit_scheduler ./visit_scheduler

FROM python:$PYTHON_VERSION AS prod

ENV VIRTUAL_ENV=/app/.venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
ENV UVICORN_WORKERS=4

COPY docker/entrypoint.sh entrypoint.sh
COPY --from=builder /app/visit_scheduler visit_scheduler
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

EXPOSE 8080

ENTRYPOINT ["bash", "entrypoint.sh"]
CMD ["run"]

FROM builder AS dev

ENV VIRTUAL_ENV=/app/.venv

COPY docker/entrypoint.sh entrypoint.sh
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --with dev
COPY --from=builder /app/visit_scheduler visit_scheduler
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

EXPOSE 8080

ENTRYPOINT ["bash", "entrypoint.sh"]
CMD ["debug"]
