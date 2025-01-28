import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

# Lista de termos a serem procurados
termos = ["termo1", "termo2", "termo3"]

# Configurações de e-mail
email_from = "seu_email@example.com"
email_to = "destinatario@example.com"
smtp_server = "smtp.example.com"
smtp_port = 587
smtp_user = "seu_email@example.com"
smtp_password = "sua_senha"

def buscar_diarios():
    url = "https://www.spdo.ms.gov.br/diariodoe"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    # Aqui você deve implementar a lógica para baixar os diários e suplementos
    # e verificar a presença dos termos.
    # Exemplo simplificado:
    for termo in termos:
        if termo in soup.text:
            enviar_email(termo, "Página X")

def enviar_email(termo, pagina):
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = f"Termo encontrado: {termo}"

    body = f"O termo '{termo}' foi encontrado na página {pagina}."
    msg.attach(MIMEText(body, 'plain'))

    # Aqui você pode anexar a página, se necessário
    # with open("pagina.pdf", "rb") as f:
    #     attach = MIMEApplication(f.read(), _subtype="pdf")
    #     attach.add_header('Content-Disposition', 'attachment', filename="pagina.pdf")
    #     msg.attach(attach)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(email_from, email_to, msg.as_string())
    server.quit()

if __name__ == "__main__":
    buscar_diarios()