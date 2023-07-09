# punch-card

## What

`punch-card` is a simple application which is run in the terminal which can be used to keep track of time spent on different activities. Currently it is still in development, hence this sparse readme

## Where

So far on MacOS and linux

### Why

TBD

### How to use

TBD

## Setup

### Required prerequisites

- MacOS/Linux
- PostgreSQL database
- use of `pyenv-virtualenv` or `conda`

First steps:

``` shell
git clone https://github.com/algrt-hm/punch-card.git
cd punch-card/
```

(then continue with setup with pyenv-virtualenv or conda below)

### Setup with pyenv-virtualenv

`punchcard` uses python 3.11.2 so first check that 3.11.2 is in the list when you run `pyenv versions`; if it is not you can run `pyenv install 3.11.2` to have this version installed.

``` shell
make pyenv-init
`make activate`
poetry install
pyenv deactivate
```

### Setup with anaconda/miniconda

To use anaconda/miniconda instead of pyenv-virtualenv

``` shell
conda create --name punch-card
conda activate punch-card

conda install -c conda-forge textual SQLAlchemy pydantic pandas psycopg2-binary
conda install -c conda-forge pytest icecream black
```

### Configuration

You then need to create `creds.toml` with the creds for the postgres database to sync to (assumed to be postgres)

``` toml
[database]

username = "database_user"
password = "database_password"
host = "database_host"
database = "database_name"
```

The database will not be created so it needs to already be set up on the PostgreSQL server with the correct permissions.