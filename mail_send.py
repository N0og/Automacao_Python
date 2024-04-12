import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from const import LOG_GERAL, CONFIG, MAIL_OPTS
from os import path

SMTP_SERVERS = {
    "outlook": {"s_address": "smtp.office365.com", "port": 587},
    "gmail": {"s_address": "smtp.gmail.com", "port": 587},
}

REMETENTE = {"automacao":
             {"name": MAIL_OPTS["HEADER"]["name"], "email": CONFIG['EMAIL']['mail_address'], "senha": CONFIG['EMAIL']['mail_password']}}

DESTINATARIO = MAIL_OPTS['EMAILS']

class MailSend:

    def __init__(self, assunto, msg, arquivo: str = "") -> None:
        LOG_GERAL.info("Tentativa de envio por e-mail...")

        self.msg = msg
        self.assunto = assunto
        self.remetente = REMETENTE["automacao"]
        self.destinatario = DESTINATARIO

        mensagem = MIMEMultipart()
        mensagem["From"] = f'{self.remetente["name"]} <{self.remetente["email"]}>'
        mensagem["To"] = ', '.join(self.destinatario.values())
        mensagem["Subject"] = self.assunto
        mensagem.attach(MIMEText(self.msg, "plain", "utf-8"))

        localArquivo = arquivo

        if path.exists(localArquivo):
            with open(localArquivo, 'rb') as relatorio:

                anexoTexto = MIMEApplication(relatorio.read())
                nome_arquivo = "Resultado de Importacao-CNES.txt"
                anexoTexto[
                    "Content-Disposition"] = f"attachment; filename={nome_arquivo}"
                mensagem.attach(anexoTexto)
        else:
            LOG_GERAL.error("Nenhum relatório atual encontrado para envio.")
            quit()

        self.send_mail(mensagem.as_string())

    def send_mail(self, mail):
        try:
            with smtplib.SMTP(SMTP_SERVERS["gmail"]["s_address"], SMTP_SERVERS["gmail"]["port"]) as servidor:
                servidor.ehlo()
                servidor.starttls()
                servidor.login(self.remetente["email"], self.remetente["senha"])
                servidor.sendmail(self.remetente["email"], list(self.destinatario.values()), mail)
        except Exception as e:
            LOG_GERAL.critical("Erro de acesso ao servidor SMTP.")
            LOG_GERAL.critical(f"{SMTP_SERVERS['gmail']}")

if __name__ == "__main__":
    pass
