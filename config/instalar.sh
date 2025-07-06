#!/bin/bash
#
# Autor: Gabriel Góes Rocha de Lima
# Data: 2024-04-28
# Versão: 0.1
#
# Descrição: Este script instala as dependências necessárias para rodar o projeto Preditor Terra.
#            Ele instala o pyenv, o pyenv-virtualenv, cria um ambiente virtual com a versão do Python desejada
#            e instala os pacotes listados em dotfiles/requirements.txt.
#
# Uso: source ./install.sh
#

# ---------------------------------------------------------------------------- #
# Função para instalar o pyenv e as dependências necessárias
install_pyenv() {
    echo ""
    echo "---------- Atualizando pacotes necessários ----------"
    if [[ "$(uname -s)" == "Linux" ]]; then
        # Define comandos de instalação baseado na distribuição
        declare -A OS_INSTALL_CMD=(
            ["/etc/arch-release"]="sudo pacman -Syu && sudo pacman -S base-devel curl git openssl zlib bzip2 readline sqlite llvm wget ncurses xz tk libffi python-pyopenssl --needed"
            ["/etc/debian_version"]="sudo apt update && sudo apt upgrade -y && sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl llvm libncurses5-dev xz-utils tk-dev libffi-dev git"
        )

        for file in "${!OS_INSTALL_CMD[@]}"; do
            if [[ -f $file ]]; then
                echo "Instalando dependências com o gerenciador encontrado..."
                eval "${OS_INSTALL_CMD[$file]}"
                break
            fi
        done

        echo ""
        echo "----------- Instalando pyenv -----------"
        curl https://pyenv.run | bash
        echo ""
        echo "pyenv instalado com sucesso."
        echo "-----------------------------------------"
    else
        echo ""
        echo "Script suportado apenas em sistemas Linux."
        return 1
    fi
}

# ---------------------------------------------------------------------------- #
# Função para instalar o pyenv-virtualenv, se necessário
install_pyenv_virtualenv() {
    echo ""
    echo "------ Verificando pyenv-virtualenv ------"
    if [[ ! -d "$(pyenv root)/plugins/pyenv-virtualenv" ]]; then
        echo ""
        echo "-------- Instalando pyenv-virtualenv --------"
        git clone https://github.com/pyenv/pyenv-virtualenv.git "$(pyenv root)/plugins/pyenv-virtualenv"
        echo ""
        echo "pyenv-virtualenv instalado."
    else
        echo ""
        echo "pyenv-virtualenv já está instalado."
        echo "---------------------------------------"
    fi
}

# ---------------------------------------------------------------------------- #
# Função que configura o pyenv e pyenv-virtualenv e adiciona a configuração ao .bash_paths
check_and_setup_pyenv_virtualenv() {
    install_pyenv
    install_pyenv_virtualenv
    # Adiciona configuração do pyenv e pyenv-virtualenv no .bash_paths, se necessário
    if ! grep -q 'pyenv init' "$HOME/.bash_paths"; then
        echo ""
        echo "Configurando pyenv..."
        {
            echo 'export PATH="$HOME/.pyenv/bin:$PATH"'
            echo 'eval "$(pyenv init --path)"'
            echo 'eval "$(pyenv virtualenv-init -)"'
        } >> "$HOME/.bash_paths"
        echo ""
        echo "Configuração do pyenv adicionada ao .bash_paths."
        # Carrega as novas configurações
        source "$HOME/.bash_paths"
    fi
}

# ---------------------------------------------------------------------------- #
# Execução principal: configura pyenv e pyenv-virtualenv
check_and_setup_pyenv_virtualenv

# ---------------------------------------------------------------------------- #
# Define o nome do ambiente virtual e a versão do Python (opções padrões: "preditor" e "3.11")
if [ $# -eq 0 ]; then
    echo ""
    echo "Escolha um nome para o ambiente virtual."
    read -p "Nome do ambiente virtual [default: preditor]: " VENV_NAME
    VENV_NAME=${VENV_NAME:-"preditor"}
    echo ""
    echo "Escolha uma versão do Python."
    read -p "Versão do Python [default: 3.11]: " PYTHON_VERSION
    PYTHON_VERSION=${PYTHON_VERSION:-"3.11"}
else
    VENV_NAME=${1:-"preditor"}
    PYTHON_VERSION=${2:-"3.11"}
fi

echo ""
echo "Configurando ambiente virtual '$VENV_NAME' com Python $PYTHON_VERSION..."

# ---------------------------------------------------------------------------- #
# Verifica e instala a versão desejada do Python via pyenv, se não existir
echo ""
echo "-> Verificando se Python $PYTHON_VERSION está instalado..."
if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo ""
    echo "! Python $PYTHON_VERSION não encontrado..."
    echo "------ Instalando Python $PYTHON_VERSION... ------"
    pyenv install "$PYTHON_VERSION"
    echo ""
    echo "------------ Python $PYTHON_VERSION instalado ------------"
else
    echo ""
    echo "Python $PYTHON_VERSION já está instalado."
    echo "--------------------------------------------"
fi

# ---------------------------------------------------------------------------- #
# Verifica e cria o ambiente virtual, se ainda não existir
echo ""
echo "-> Verificando se o virtualenv '$VENV_NAME' existe..."
if ! pyenv virtualenvs | grep -q "$VENV_NAME"; then
    echo "! Virtualenv '$VENV_NAME' não encontrado..."
    echo ""
    echo "------ Criando virtualenv '$VENV_NAME' com Python $PYTHON_VERSION... ------"
    pyenv virtualenv "$PYTHON_VERSION" "$VENV_NAME"
    echo "-------------- Virtualenv criado --------------"
    echo ""
else
    echo "Virtualenv '$VENV_NAME' com Python $PYTHON_VERSION já existe."
    echo "---------------------------------------------"
fi

# ---------------------------------------------------------------------------- #
# Configuração do ambiente local para o repositório
echo "-> Configurando ambiente local para o repositório com pyenv..."
pyenv local "$VENV_NAME"

# ---------------------------------------------------------------------------- #
# Adiciona a configuração do .bash_paths ao .bash_profile ou .profile, se necessário
echo "-> Adicionando .bash_paths à configuração do shell..."
for file in "$HOME/.bash_profile" "$HOME/.profile"; do
    if [[ -f "$file" ]]; then
        if ! grep -q '\.bash_paths' "$file"; then
            echo "source \$HOME/.bash_paths" >> "$file"
            echo "Configuração adicionada a $file."
        fi
        source "$file"
    fi
done

# ---------------------------------------------------------------------------- #
# Instalação das dependências Python
echo ""
echo "Instalando dependências Python..."
pip install -r "./dotfiles/requirements.txt"

# Caso queira instalar o projeto como pacote editável, se aplicável:
pip install -e .

echo ""
echo "Instalação concluída com sucesso!"
echo ""
echo "Para efetivar as mudanças, reinicie o terminal ou execute: source \$HOME/.bash_profile"
echo "Em seguida, navegue até o diretório do projeto e verifique o ambiente virtual com:"
echo "   pyenv local $VENV_NAME"
