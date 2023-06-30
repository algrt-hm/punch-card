#!/bin/bash

ENVNAME="punch-card"

f-setup-pyenv() {
    # https://stackoverflow.com/a/677212
    if ! command -v pyenv &>/dev/null; then
        echo "pyenv not found"
    else
        # See https://github.com/pyenv/
        alias brew='env PATH="${PATH//$(pyenv root)\/shims:/}" brew'
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init --path)"
        eval "$(pyenv init -)"

        # See https://github.com/pyenv/pyenv-virtualenv
        eval "$(pyenv virtualenv-init -)"
    fi
}

f-setup-pyenv

if [[ $PYENV_VERSION = "$ENVNAME" ]]; then
    echo "$ENVNAME activated already"
else
    PYENV_VIRTUALENV_DISABLE_PROMPT=1 pyenv activate $ENVNAME
fi

python src/main.py "$@"
