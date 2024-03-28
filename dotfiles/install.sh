#!/bin/bash
#
# Author: Gabriel Góes Rocha de Lima
# Date: 2024-03-28
#
# Description: This script installs the necessary dependencies to run the project.
# Usage: ./install.sh
#

# Configuração inicial
VENV_NAME="discrim"
PYTHON_VERSION="3.7.9"
REQUIREMENTS_FILE="./discrim_requirements.txt"

# Função para instalar pyenv
install_pyenv() {
    echo ' Instalando pyenv...'
    sudo apt-get update
    sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils \
    tk-dev libffi-dev liblzma-dev python-openssl git

    curl https://pyenv.run | bash

    # Configuração do pyenv no .bashrc/.zshrc
    {
        echo 'export PATH="$HOME/.pyenv/bin:$PATH"'
        echo 'eval "$(pyenv init --path)"'
    } >> ~/.bashrc
    source ~/.bashrc
}

# Função para instalar pyenv-virtualenv
install_pyenv-virutalenv() {
    echo ' Instalando pyenv-virtualenv...'
    # Instala o pyenv-virtualenv
    git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv

    if ! grep -q 'pyenv virtualenv-init' ~/.bashrc; then
        echo 'eval "$(pyenv virtualenv-init -)"'>> ~/.bashrc
        source ~/.bashrc
    fi
}

echo 'Verificando se pyenv está instalado...'
if "$(pyenv root)" > /dev/null 2>&1; then
    install_pyenv
    install_pyenv-virutalenv
else
    echo 'pyenv já está instalado.'
    echo '--------------------------'
    echo ' '
fi

echo 'Verificando se pyenv-virtualenv está instalado...'
if [ ! -d "$(pyenv root)/plugins/pyenv-virtualenv" ]; then
    install_pyenv-virutalenv
else
    echo 'pyenv-virtualenv já está instalado.'
    echo '--------------------------'
    echo ' '
fi

if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    pyenv install $PYTHON_VERSION
fi
