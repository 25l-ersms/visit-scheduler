# Visit scheduler

## Design

Api docs: http://localhost:8080/docs # swagger is the best docs
Overall functionalities description:
- kafka consumer:
  - add_vendor: adding vendor information from kafka, has to make a local cache of vendors 
  - add_rating: add rating about vendor from kafka
- endpoints:
  - add_time_slot: vendor adding time slot
  - search_visit: client searching visit
- saving visit into visit_manager by using its api


## Development

### Dependencies

The project manager used is [Poetry](https://python-poetry.org/) (version `>=2.0.0`).
It has to be installed and used in order to correctly add dependencies to the project.

Python `^3.11` is required. Install using [`pyenv`](https://github.com/pyenv/pyenv) (don't forget about [build dependencies](https://github.com/pyenv/pyenv)!):

```shell
pyenv install 3.11
```

Install the project in a local virtual environment:
```shell
PYENV_VERSION=3.11 python3 -m venv .venv
VIRTUAL_ENV=.venv poetry install --with dev
```

### Build

```shell
# production environment
docker build -t visit-scheduler:latest --target=prod .

# development environemnt (includes pytest, ruff, mypy and hot-reload)
docker build -t visit-scheduler:dev --target=dev .
```

### Development

# Dev variables defined in .env in dev-ops repo

- ES_HOST
- ES_LOGIN
- ES_PASS
- UVICORN_WORKERS
- KAFKA_BOOTSTRAP_URL
- KAFKA_GROUP_ID
- KAFKA_TOPIC
- KAFKA_AUTHENTICATION_SCHEME

#### Running the app

Run locally:

```shell
poetry run uvicorn --reload visit_scheduler.app.main:app --port 8080
 ```

Run the dev image with hot reload:

```shell
docker run -it --env-file=.env \
    --mount type=bind,src=$(pwd)/visit_scheduler,dst=/app/visit_scheduler \
    visit-scheduler:dev
```

Run the prod image:

```shell
docker run -it --env-file=.env visit-scheduler:latest
```

#### Contributing

Install [pre-commit](https://pre-commit.com/) hooks (`pre-commit` itself is installed as a dev dependency by `poetry`):

```shell
poetry run pre-commit install
```

or run checks manually (remember, they will run in CI anyway!):

```shell
# verify pyproject.toml integrity
poetry check
# run tests
poetry run pytest
# run ruff check
poetry run ruff check [--fix]
# run mypy
poetry run mypy .
# reformat code
poetry run ruff format
```
