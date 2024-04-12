from os import path, getcwd, _exit, makedirs
from datetime import datetime
import json
import logging
import configparser

class Function:
    def load_json(_json):
        try:
            with open(path.join(JSON_PATH, _json), 'r') as json_file:
                return json.load(json_file)
        except Exception as e:
            raise e
        
    def check_exists_dir(_path):
        if not path.exists(_path):
            makedirs(_path)
            _pasta_falta = _path.split(_path)[1]
            logging.warning(
                f"Pasta {_pasta_falta}, não encontrada. Criada em momento de execução... | *Risco de falha na integridade de dados do BOT.*"
            ) 

    def configure_logs(log, log_path):
        log.setLevel(logging.INFO)
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        log.addHandler(handler)


MAIN_PATH = getcwd()

CONFIG_PATH = path.join(MAIN_PATH, 'config')
Function.check_exists_dir(CONFIG_PATH)

JSON_PATH = path.join(CONFIG_PATH, 'json')
Function.check_exists_dir(JSON_PATH)

LOGS_PATH = path.join(MAIN_PATH, "logs")
Function.check_exists_dir(LOGS_PATH)

LOG_GERAL = logging.getLogger("main_log")
LOG_GERAL_PATH = path.join(LOGS_PATH, f'process-{datetime.today().strftime("%d-%m-%Y")}.log')
Function.configure_logs(LOG_GERAL, LOG_GERAL_PATH)

LOG_ERROR = logging.getLogger("error_log")
LOG_ERROR_PATH = path.join(LOGS_PATH, f'process-errors-{datetime.today().strftime("%d-%m-%Y")}.log')
Function.configure_logs(LOG_ERROR, LOG_ERROR_PATH)

XML_PATH = path.join("-->PASTA ONDE ESTÃO OS XML's CNES.<--")

DATA_ATUAL = datetime.today().strftime("%Y-%m-%d")

PEC_IPS = Function.load_json('pec.json')
EAS_HOSTS = Function.load_json('retaguarda.json')
MAIL_OPTS = Function.load_json(path.join('mail_opts', 'mail.json'))

CONFIG_FILE = path.join(CONFIG_PATH, "config.ini")

if not path.exists(CONFIG_FILE):
    logging.critical(f"{CONFIG_FILE} comprometido.")
    _exit(0)
else:
    CONFIG = configparser.ConfigParser()
    CONFIG.read(CONFIG_FILE)
