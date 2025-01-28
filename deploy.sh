#!/bin/bash

# Configurações
SCRIPT_DIR="/opt/diario_automation"
SCRIPT_NAME="main.py"
SERVICE_NAME="diario.service"
GITHUB_REPO="git@github.com:marcioimai/doems.git"

# Atualiza o sistema e instala dependências
echo "Atualizando o sistema e instalando dependências..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip git
sudo apt install python3-requests python3-bs4 python3-lxml -y

# Cria o diretório para o script
echo "Criando diretório para o script..."
sudo mkdir -p $SCRIPT_DIR
sudo chown -R ubuntu:ubuntu $SCRIPT_DIR

# Clona o repositório do GitHub
echo "Clonando o repositório do GitHub..."
cd $SCRIPT_DIR
git clone $GITHUB_REPO .
############################## até aqui ok ##############################

# Cria o arquivo de serviço systemd
echo "Criando o serviço systemd..."
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME" <<EOF
[Unit]
Description=Serviço de automação do Diário Oficial
After=network.target

[Service]
ExecStart=/usr/bin/python3 $SCRIPT_DIR/$SCRIPT_NAME
Restart=always
User=ubuntu

[Install]
WantedBy=multi-user.target
EOF

# Recarrega o systemd e habilita o serviço
echo "Recarregando o systemd e habilitando o serviço..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Verifica o status do serviço
echo "Verificando o status do serviço..."
sudo systemctl status $SERVICE_NAME

echo "Configuração concluída com sucesso!"