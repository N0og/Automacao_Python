from const import LOG_GERAL_PATH, LOG_ERROR_PATH, MAIL_OPTS
import mail_send
from datetime import datetime


def read_log():

    errors = 0
    warnings = 0
    criticals = 0

    with open(LOG_GERAL_PATH, 'r') as log:
        linhas = log.readlines()
        
        for linha in linhas:
            if "ERROR" in linha:
                errors +=1

            elif "WARNING" in linha:
                warnings += 1

            elif "CRITICAL" in linha:
                criticals += 1

    return f"\
Prezados,\n\n\
\
Informo que a importação automática do CNES XML ocorreu hoje às {datetime.today().strftime('%d/%m/%Y, %H:%M:%S')}.\n\n\
\
Ao final do processo, obtivemos:\n\n\
\
{errors} - Unidades não processadas.\n\
{warnings} - Alertas durante o processo.\n\
{criticals} - Erros Criticos na execução da automação.\n\
\n\n\
\
Totalizando: {(errors+warnings+criticals)} inconsistências no processo.\n\n\
\
Lembramos que o correto funcionamento do processo está condicionado à existência de uma conexão ativa na unidade onde a plataforma opera.\n\
Portanto, é possível que eventuais erros e inconsistências durante o processo estejam relacionados à ausência de conectividade de rede.\n\n\
\
Recomendamos a análise do histórico de erros pontuados durante processo, o qual está anexado a esta mensagem, a fim de compreender os incidentes ocorridos.\n\n\
\
Dados Técnicos:\n\
- Nome: Automação XML-CNES\n\
- Versão: v2.0\n\n\
\
Este e-mail tem caráter informativo e foi gerado automaticamente. Por favor, não responda a este e-mail.\n\n\
\
Atenciosamente,\n\n\
\
-->SEU NOME AQUI<--."

def enviar_log():
    mail_send.MailSend(MAIL_OPTS['HEADER']['subject'], read_log(), arquivo=LOG_ERROR_PATH)

if __name__ == '__main__':
    enviar_log()
