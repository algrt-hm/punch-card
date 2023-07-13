.POSIX:

project_name = punch-card
python_version = 3.11.2
sqlite = sqlite3 $(project_name).sqlite3

all: run

clean:
	rm *.vcs

read-state:
	@$(sqlite) \
	"select * from timer_state;"

read-log:
	@$(sqlite) \
	"select * from timer_log;"

sql:
	$(sqlite)

test:
	python -m pytest -s

run:
	python src/main.py

sync:
	python src/sync_dbs.py

format:
	black \
	--line-length 200 \
	src/*.py tests/*.py

pyenv-init:
	pyenv virtualenv $(python_version) $(project_name)

poetry-init:
	poetry install

activate:
	@echo pyenv activate $(project_name)

help:
	@printf 'TODO: Help here!\n'
