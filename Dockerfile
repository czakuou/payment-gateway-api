FROM python:3.12-slim-bookworm as python-base

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /src


FROM python-base as dependencies-base

ENV POETRY_VERSION=1.8.2

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl

RUN curl -sSL https://install.python-poetry.org | python - \
    && $HOME/.local/bin/poetry self add poetry-plugin-export

COPY ./poetry.lock ./pyproject.toml ./


FROM dependencies-base as dependencies-dev

RUN --mount=type=cache,target=/root/.cache/pip \
    $HOME/.local/bin/poetry export -o requirements.txt --with dev \
    && pip install -r requirements.txt --prefix dependencies

FROM dependencies-base as dependencies-prod

RUN --mount=type=cache,target=/root/.cache/pip \
    $HOME/.local/bin/poetry export -o requirements.txt \
    && pip install -r requirements.txt --prefix dependencies


FROM python-base as dev

CMD ["uvicorn", "src.core.fastapi:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EXPOSE 8000

COPY --from=dependencies-dev /src/dependencies /usr/local
COPY . .


FROM python-base as prod

CMD ["gunicorn", "-c", "gunicorn.conf.py", "src.core.fastapi:app"]
EXPOSE 8000

ARG VERSION
ENV VERSION=$VERSION

COPY --from=dependencies-prod /src/dependencies /usr/local
COPY gunicorn.conf.py .
COPY src src
