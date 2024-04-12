from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from ExceptionClass import *
import os
from const import LOG_GERAL
import time
from navigator import *

# --> Verifica se o browser está instalado.
def check_browser_installed(browser_path: str):
    if os.path.exists(browser_path):
        return True
    else:
        return False

class RetaguardaBOT:
    # --> Instancia o BOT Agente.
    def __init__(self, cliente: tuple, cliente_nome: str, carga: str = "") -> None:

        # Atributos

        self.host = "http://"+cliente[0]+cliente[1]+".esusatendsaude.com.br"

        self.municipio = cliente_nome
        self.carga = os.path.abspath(carga)

        # Carregamento do WebDriver.
        try:
            self.driver = self.load_webdriver()
        except BrowserNotFoundError as e:
            LOG_GERAL.critical(e)
            os._exit(0)

        # Entrando no Host-Retaguarda.
        try:
            self.home()
        except BadConection as e:
            raise DriverInterrupted(e)
        
        self.wait = WebDriverWait(self.driver, 10)
        
     # --> Carregando o Navegador disponível para coletar o webdriver base.
    def load_webdriver(self) -> webdriver.Chrome: 
        browsers_paths = [
            {
                "name": "Chrome",
                "paths": [
                    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                    r'C:\Program Files\Google\Chrome\Application\chrome.exe'
                ],
                "function": chrome_nav
            },
            {
                "name": "Edge",
                "paths": [
                    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
                ],
                "function": edge_nav
            }
        ]

        for browser in browsers_paths:
            if any(check_browser_installed(path) for path in browser["paths"]):
                LOG_GERAL.info(f"{browser['name']} selecionado.")
                return browser["function"]()

        LOG_GERAL.critical("Navegador compatível não disponível em sistema.")
        raise BrowserNotFoundError("Navegador compatível não disponível em sistema.")

    # --> Acesso ao home do Retaguarda.
    def home(self) -> bool:  
        try:
            self.driver.get(self.host)
        except Exception as e:
            raise BadConection("Conexão com o host mau sucedido.")

        LOG_GERAL.info(f"+==INICIO DE EXTRAÇÃO: {self.municipio}!==+")
        LOG_GERAL.info(f"HOME: {self.municipio}")
        LOG_GERAL.info("Acesso ao RETAGUARDA realizado.") 
        return True
    
    # --> Acesso ao URL específico do Retaguarda.
    def goto(self, address) -> bool: 
        try:
            self.driver.get(f"{self.host}/{address}")
            return True
        except:
            LOG_GERAL.critical(f"Erro de conexão! - URL: {address}")
            raise BadConection("Carregamento mau sucedido.")

    # --> Realiza o Login.
    def login(self, username: str, password: str):
        """
        Realiza o login.\n
        Se caso erro durante o processo, será apresentado no log de saída.
        """
        try:

            self.driver.find_element(By.NAME, value='UserName').send_keys(username)
            self.driver.find_element(By.NAME, value='Senha').send_keys(password)

            checkbox = self.driver.find_element(
                By.ID, 'TermoConfiabilidadePrivacidade')
            checkbox.click()

            login_button = self.driver.find_element(By.ID, value='btn')
            login_button.click()

            login_wait = WebDriverWait(self.driver, 3)

            try:
                login_wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'validation-summary-errors')))
                return False

            except TimeoutException as e:
                LOG_GERAL.info("Login Efetuado.")
                return True

        except Exception as e:
            self.interrupt_driver()
            raise DriverInterrupted("Erro na pagina de login.")

    def importar_xml(self) -> bool:
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "modalAviso")))
            self.driver.execute_script('document.getElementById("modalAviso").remove();')
            self.driver.execute_script('document.getElementsByClassName("modal-backdrop fade in")[0].remove();')
            self.driver.execute_script(
            'document.querySelector(".navbar-fixed-bottom.versao").remove();')
        
            input_file = self.wait.until(EC.presence_of_element_located((By.ID, 'valueFile')))
            input_file.send_keys(self.carga)
            self.wait_load_table()
            btn = self.driver.find_element(By.XPATH, '//*[@id="importa-xml"]/div/div[3]/div/div/button')
            btn.click()
            LOG_GERAL.info(f"Tentativa de Importação Retaguarda: {self.municipio.upper()}...")
            self.wait_import()
            self.interrupt_driver()
            return True
        except TimeoutException:
            self.interrupt_driver()
            raise DriverInterrupted('Falha na página de ImportarXML.')
        
    def wait_load_table(self) -> bool:
        while True:
            tabela = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="importa-xml"]/div/div[2]/div/form/div[3]/table')))
            profissionais = tabela.find_elements(By.TAG_NAME, 'tbody')

            if profissionais:
                    break

    def wait_import(self) -> bool:
        time.sleep(5)
        while True:
                loading_obj = self.driver.find_element(By.XPATH, '//*[@id="pleaseWaitDialog"]')
                classe = loading_obj.get_attribute('class')

                if classe == 'modal fade in':
                    continue
                else:
                    LOG_GERAL.info(f"Importação Concluida Retaguarda: {self.municipio.upper()}...")
                    break

    # --> Encerra o BOT.
    def interrupt_driver(self):
        LOG_GERAL.info("+==BOT ENCERRADO!==+")
        self.driver.quit()