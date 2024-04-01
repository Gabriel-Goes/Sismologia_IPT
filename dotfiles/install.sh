#!/bin/bash
#
# Author: Gabriel Góes Rocha de Lima
# Date: 2024-03-28
# Version: 0.1
#
# Description: This script installs the necessary dependencies to run the project.
# Usage: source ./install.sh
#

# ---------------------------------------------------------------------------- #
# Função para instalar pyenv
install_pyenv() {
    echo ''
    echo ' ---------- Atualizando pacotes necessários ------------ '
    if [[ "$(uname -s)" == "Linux" ]]; then
        # Define comandos de instalação baseado na distribuição
        declare -A OS_INSTALL_CMD=(
            ["/etc/arch-release"]="sudo pacman -Syu && sudo pacman -S docker base-devel openssl zlib bzip2 readline sqlite curl llvm wget ncurses xz tk libffi python-pyopenssl git --needed"
            ["/etc/debian_version"]="sudo apt update && sudo apt upgrade -y && sudo apt install -y docker build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev python-openssl git"
        )

        for file in "${!OS_INSTALL_CMD[@]}"; do
            if [[ -f $file ]]; then
                eval "${OS_INSTALL_CMD[$file]}"
                break
            fi
        done
        
        echo ''
        echo ' -----------  Instalando pyenv ------------ '
        curl https://pyenv.run | bash
        echo ''
        echo '              pyenv instalado               '
        echo ' -------------------------------------------'
    else
        echo ''
        echo 'Script suportado apenas em sistemas Linux.'
        return 1
    fi
}

install_pyenv_virtualenv() {
    echo ''
    echo ' -------- Verificando pyenv-virtualenv ------------'
    if [[ ! -d "$(pyenv root)/plugins/pyenv-virtualenv" ]]; then
        echo ''
        echo ' ---------- Instalando pyenv-virtualenv ------------'
        git clone https://github.com/pyenv/pyenv-virtualenv.git "$(pyenv root)/plugins/pyenv-virtualenv"
        echo ''
        echo 'pyenv-virtualenv instalado.'
    else
        echo ''
        echo 'pyenv-virtualenv já está instalado.'
        echo ' --------------------------------------- '
    fi
}

check_and_setup_pyenv_virtualenv() {
    install_pyenv
    install_pyenv_virtualenv
    # Adiciona configuração do pyenv e pyenv-virtualenv ao .bash_paths, se necessário
    if ! grep -q 'pyenv init' $HOME/.bash_paths; then
        echo ''
        echo ' Configurando pyenv...'
        {
            echo 'export PATH="$HOME/.pyenv/bin:$PATH"'
            echo 'eval "$(pyenv init --path)"'
            echo 'eval "$(pyenv virtualenv-init -)"'
        } >> $HOME/.bash_paths
        echo ''
        echo 'Configuração do pyenv adicionada ao .bash_paths.'
        source $HOME/.bash_paths
    fi

}

# Principal: executa a configuração
check_and_setup_pyenv_virtualenv
# Definindo Versão do python e nome do ambiente virtual
if [ $# -eq 0 ]; then
    echo ''
    echo "Escolha um nome para o ambiente virtual."
    read -p "Nome do ambiente virtual [default: sismologia]: " VENV_NAME
    VENV_NAME=${VENV_NAME:-"sismologia"}
    echo ''
    echo "Escolha uma versão do Python."
    read -p "Versão do Python [default: 3.11]: " PYTHON_VERSION
    PYTHON_VERSION=${PYTHON_VERSION:-"3.11"}
else
    VENV_NAME=${1:-"sismologia"}
    PYTHON_VERSION=${2:-"3.11"}
fi
echo ''
echo "Configurando ambiente virtual '$VENV_NAME' com Python $PYTHON_VERSION..."

# Instalando Python $PYTHON_VERSION
echo ''
echo " -> Verificando se  Python $PYTHON_VERSION existe..."
if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo ''
    echo " ! $PYTHON_VERSION não existe..."
    echo ''
    echo " ------ Instalando Python $PYTHON_VERSION... ------"
    pyenv install $PYTHON_VERSION
    echo ''
    echo " ------------ Python $PYTHON_VERSION instalado ------------"
else
    echo ''
    echo "Python $PYTHON_VERSION já está instalado."
    echo '-----------------------------------------'
fi

# Criando ambiente virtual $VENV_NAME
echo ''
echo " -> Verificando se virtualenv com Python$PYTHON_VERSION existe..."
if ! pyenv virtualenvs | grep -q "$PYTHON_VERSION"; then
    echo " ! virtualenv com Python$PYTHON_VERSION não existe..."
    echo ''
    echo " ------ Criando virtualenv com Python$PYTHON_VERSION... ------"
    pyenv virtualenv $PYTHON_VERSION $VENV_NAME
    echo ' -------------- Virtualenv criado --------------'
    echo ''
else
    echo "Virtualenv com Python$PYTHON_VERSION já existe."
    echo '--------------------------'
    echo ''
fi

# Adicionando variáveis de ambiente ao .bashrc
echo ' -> Adicionando .bash_paths ao .bash_profile...'
# Verifica se é .profile ou .bash_profile
find $HOME -maxdepth 1 -name '.*profile' | while read -r file; do
    if ! grep -q '.bash_paths' $file; then
        echo 'Adicionando .bash_paths ao '$file'...'
        echo 'source $HOME/.bash_paths' >> $file
    fi
    source $file
done
echo ' ------------------------------------ '

echo ' Instalação concluída com sucesso!'
echo ' Para efetivar as mudanças reinicie o terminal:'
echo ' ! AVISO ! Variáveis de ambiente definidas neste Shell serão perdidas.'
read -p 'Pressione enter para continuar...'

source $HOME/.bash_profile
echo 'Ambiente virtual configurado com sucesso!'
echo 'Navegue até o diretório do projeto e execute:'
echo '`pyenv local $VENV_NAME` para ativar o ambiente virtual.'
# ---------------------------------------------------------------------------- #
