import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv
import PyPDF2
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import resend
import base64
from datetime import datetime

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Lista de termos a serem procurados
termos = ["termo1", "termo2", "termo3"]

# Configurações de email do arquivo .env
email_from = os.getenv("EMAIL_FROM")
email_to = os.getenv("EMAIL_TO")

def baixar_pdf(url):
    print(f"Baixando PDF: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    return None

def ler_pdf(pdf_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        texto_completo = ""
        for pagina in pdf_reader.pages:
            texto_completo += pagina.extract_text()
        return texto_completo
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return ""

def buscar_diarios():
    # Configurar o Chrome em modo headless (sem interface gráfica)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--ignore-certificate-errors')
    options.binary_location = "/snap/bin/chromium"
    
    # Configurar o driver
    service = Service(ChromeDriverManager(chrome_type="chromium").install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = "https://www.spdo.ms.gov.br/diariodoe"
        print(f"Acessando URL: {url}")
        driver.get(url)
        
        # Obter a data atual no formato DD/MM/YYYY
        data_atual = datetime.now().strftime("%d/%m/%Y")
        print(f"Buscando diários da data: {data_atual}")
        
        # Esperar pelos links dos diários
        wait = WebDriverWait(driver, 10)
        links_diarios = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "abrirDiario"))
        )
        
        # Filtrar apenas os links com a data atual
        links_hoje = [link for link in links_diarios if link.text.strip() == data_atual]
        
        if not links_hoje:
            print(f"Nenhum diário encontrado para a data {data_atual}")
            return
            
        print(f"Encontrados {len(links_hoje)} diários para hoje")
        
        for link in links_hoje:
            try:
                # Clicar no link para abrir o PDF
                print(f"Clicando no link do diário de {link.text.strip()}...")
                link.click()
                
                # Esperar um pouco para o PDF carregar em uma nova aba
                time.sleep(2)
                
                # Mudar para a nova aba
                abas = driver.window_handles
                if len(abas) > 1:
                    driver.switch_to.window(abas[-1])
                    
                    # Pegar a URL do PDF
                    pdf_url = driver.current_url
                    print(f"URL do PDF: {pdf_url}")
                    
                    # if pdf_url and pdf_url.endswith('.pdf'):
                    if pdf_url:
                        # Baixa e lê o PDF
                        pdf_bytes = baixar_pdf(pdf_url)
                        if pdf_bytes:
                            texto_pdf = ler_pdf(pdf_bytes)
                            
                            # Busca os termos no texto do PDF
                            for termo in termos:
                                if termo.lower() in texto_pdf.lower():
                                    print(f"Termo '{termo}' encontrado no diário: {pdf_url}")
                                    enviar_email(termo, pdf_url, pdf_bytes)
                    
                    # Fechar a aba do PDF
                    driver.close()
                    
                    # Voltar para a aba principal
                    driver.switch_to.window(abas[0])
                
            except Exception as e:
                print(f"Erro ao processar link: {e}")
                continue
                
    finally:
        # Fechar o navegador
        driver.quit()

def enviar_email(termo, pdf_url, pdf_bytes):
    print(f"Enviando e-mail para {email_to} com o assunto: {f'Termo encontrado: {termo}'}")
    
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        
        # Criar o email como HTML para melhor formatação
        html_content = f"""
        <h2>Termo encontrado no Diário Oficial</h2>
        <p>O termo '<strong>{termo}</strong>' foi encontrado no diário:</p>
        <p><a href="{pdf_url}">Link para o diário</a></p>
        """
        
        # Converter bytes para base64
        pdf_base64 = base64.b64encode(pdf_bytes.getvalue()).decode('utf-8')
        
        # Enviar o email usando o Resend
        # r = resend.Emails.send({
        #     "from": email_from,
        #     "to": email_to,
        #     "subject": f"Termo encontrado: {termo}",
        #     "html": html_content,
        #     "attachments": [{
        #         "filename": "diario.pdf",
        #         "content": pdf_base64,
        #         "content_type": "application/pdf"
        #     }]
        # })
        
        print("Email enviado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao enviar email: {e}")

if __name__ == "__main__":
    buscar_diarios()