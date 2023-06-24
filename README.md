# punch-card

## What

`punch-card` is a simple application which is run in the terminal which can be used to keep track of time spent on different activities. Currently it is still in development, hence the sparse readme

## Where

So far on MacOS and linux

### Why

TBD

### How to use

TBD

## Setup

### With pyenv-virtualenv

``` shell
make pyenv-init
`make activate`
make poetry-init
```

### With anaconda/miniconda

``` shell
conda create --name punch-card
conda activate punch-card

conda install -c conda-forge textual SQLAlchemy pydantic pandas psycopg2-binary
conda install -c conda-forge pytest icecream black
```