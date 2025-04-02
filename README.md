# Visit scheduler

## Development

### Dependencies

The project manager used is [Poetry](https://python-poetry.org/) (version `>=2.0.0`). 
It has to be installed and used in order to correctly add dependencies to the project.

Python `^3.11` is required. Install using [`pyenv`](https://github.com/pyenv/pyenv) (don't forget about [build dependencies](https://github.com/pyenv/pyenv)!):

```shell
pyenv install 3.11
```

Install the project in a local virtual environemnt:

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

#### Running the app 

Copy the sample envfile:

```shell
cp .env.sample .env
```

Run locally:

```shell
poetry run uvicorn --reload visit_scheduler.app.main:app --port 8080
 ```

Run the dev image:

```shell
docker run -it --env-file=.env visit-scheduler:dev
```

Run the prod image:

```shell
docker run -it --env-file=.env visit-scheduler:latest
```

#### Contributing

Install [pre-commit](https://pre-commit.com/) hooks:

```shell
pre-commit install
```

or run checks manually:

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