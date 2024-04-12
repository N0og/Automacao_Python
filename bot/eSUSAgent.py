from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, InvalidArgumentException
from ExceptionClass import *
import os
from time import sleep
from datetime import datetime
from const import LOG_GERAL
from navigator import *

TEMPO_RESPOSTAS = {"short":3,
                   "mid": 6,
                   "long": 10,
                   "wait_request": 360}

# --> Verifica se o browser está instalado.
def check_browser_installed(browser_path:str):
    if os.path.exists(browser_path):
        return True
    else: 
        return False

class eSUSBOT:
    
    """
    Instancía o BOT Agente que irá carregar o XML para a aba CNES do eSUS através do perfil administrador municipal.\n
    ARGS NECESSÁRIOS:\n
    1 - tupla(Ip e Porta);\n
    2 - tupla(Nome do município e unidade);\n
    3 - endereço do XML direcionado pelo Manager."""

    def __init__(self, address:tuple, cliente:tuple, carga:str, xml_opt:str = 'cnes') -> None:

        #Atributos.
        self._host = 'http://'+ address[0] +':'+ address[1]
        self._port = address[1] 
        self._municipio = cliente[0].lower() 
        self._unidade = cliente[1].lower()
        self._xml_opt = xml_opt
        self._carga = os.path.abspath(carga) 
        
        # Carregamento do WebDriver.
        try:
            self.driver = self.load_webdriver()
        except BrowserNotFoundError as e:
            LOG_GERAL.critical(e)
            os._exit(0)

        #Entrando no Host-eSUS.
        try:
            self.acess_eSUS()
        except BadConection as e:
            self.interrupt_driver()
            raise DriverInterrupted(e)
        
        self._shortWait = WebDriverWait(self.driver, TEMPO_RESPOSTAS["short"])
        self._midWait = WebDriverWait(self.driver, TEMPO_RESPOSTAS["mid"])
        self._longWait = WebDriverWait(self.driver, TEMPO_RESPOSTAS["long"])
        self._debbugWait = WebDriverWait(self.driver, 500)

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

    # --> Acesso ao URL do eSUS.
    def acess_eSUS(self) -> bool:
        try:
            self.driver.get(self._host)    
        except Exception as e:
            raise BadConection("Conexão com o host mau sucedido.")
        
        LOG_GERAL.info(f"+==INICIO DE IMPORTAÇÃO {self._xml_opt.upper()} - {self._municipio.upper()} - {self._unidade}!==+")
        LOG_GERAL.info(f"+==CONFIGS: {self._host}==+")
        LOG_GERAL.info("Acesso ao eSUS realizado.")
        return True

    # --> Acesso ao URL específico.
    def goto(self, address) -> bool: 
        try:
            self.driver.get(f"{self._host}/{address}")
            return True
        except:
            self.interrupt_driver()
            raise DriverInterrupted(f"Acesso a: {address} mau sucedido.")
    

    #AÇÕES DA AUTOMAÇÃO SOLICITADAS PELO USUÁRIO.

    # --> Realiza o Login e se efetuado com sucesso, dá início as solicitações.
    def login(self, username:str, password:str) -> bool:

        """
        Realiza o login no eSUS AB.\n
        se caso erro durante o processo, será apresentado no log de saída.
        """
        try:
            campo_user = self.driver.find_element(By.NAME, value='username')
            campo_senha = self.driver.find_element(By.NAME, value='password')
            
            campo_user.clear()
            campo_senha.clear()

            campo_user.send_keys(username)
            campo_senha.send_keys(password)
            
            login_button = self.driver.find_element(By.CLASS_NAME, value='css-1mc6ylg')
            login_button.click() 

            try:
                self._shortWait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'css-1prlhy')))
                return False
            
            except TimeoutException as e:
                LOG_GERAL.info("Login Efetuado.")
                try:
                    self._longWait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'css-18soxw1')))
                    
                    continue_button = self.driver.find_element(By.CLASS_NAME, value='css-1jy51ie')
                    continue_button.click()
                    return True

                except TimeoutException as e:
                    return True
                       
        except Exception:
            self.interrupt_driver()
            raise DriverInterrupted("Erro na pagina de login.")

    # --> Realiza a busca e seleção do perfil Administrador Municipal.
    def select_profile(self, municipio, profile) -> bool:
        try:
            perfis = self._midWait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.css-wstido div[data-cy="Acesso.card"]')))

            for perfil in perfis:
                nomeDoPerfil = perfil.accessible_name.lower()
                if municipio.lower() in nomeDoPerfil and profile.lower() in nomeDoPerfil:
                    perfil.click()
                    LOG_GERAL.info(f"Acesso ao perfil {self._municipio} | 'Administrador Municipal' efetuado.")
                    return True
                
            self.interrupt_driver()
            raise DriverInterrupted("Perfil ADM não localizado.")

        except TimeoutException:
            return True
            #self.interrupt_driver()
            #raise DriverInterrupted("Perfis não localizados.")
        
    # --> Responsável por enviar o XML para o INPUT.
    def importar_xml(self) -> bool:
            try:
                input_file = self._midWait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.css-9lbswl input[type="file"]')))

                try:
                    input_file.send_keys(self._carga)
                    LOG_GERAL.info(f"Tentativa de Importação {self._municipio.upper()} - {self._unidade.upper()}...")
                    try:
                        self._midWait.until_not(EC.presence_of_element_located((By.CLASS_NAME, 'css-16cvhsb')))
                    except TimeoutException:
                        self.interrupt_driver()
                        raise DriverInterrupted('XML Fora de conformidado com modelo CNES --> eSUS.')

                    LOG_GERAL.info(f"Importação realizada: {self._municipio.upper()} - {self._unidade.upper()}...")
                    return True
                
                except InvalidArgumentException:
                    self.interrupt_driver()
                    raise DriverInterrupted("Carga inválida para inserção.")

            except TimeoutException:
                self.interrupt_driver()
                raise DriverInterrupted("Erro na Pagina do CNES.")

    # --> Informa o resultado do INPUT.
    def result(self):
        try:
            loading_div = self._longWait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-zbf35q')))
            progress = self._longWait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-1ip3lkc')))
            finish_progress = self._debbugWait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-a9z75u')))
            self.goto('importarCnes')
            self.check_backdrop()
            result = self.wait_result()                  
        
            if result:
                LOG_GERAL.info("ULTIMA ATUALIZAÇÃO DE IMPORTAÇÃO PRESENTE EM SISTEMA:")
            
                if result[2].lower() == 'falha':
                    LOG_GERAL.warning(f"DATA: {result[0]}, SITUAÇÃO: {result[2]}, EQUIPES: {result[3]}, PROFISSIONAIS: {result[4]}, LOTAÇÕES: {result[5]}")
                    LOG_GERAL.warning("Importação mal sucedida!")

                else:
                    LOG_GERAL.info(f"DATA: {result[0]}, SITUAÇÃO: {result[2]}, EQUIPES: {result[3]}, PROFISSIONAIS: {result[4]}, LOTAÇÕES: {result[5]}")
                    LOG_GERAL.info("Importação bem sucedida!")
            else:
                LOG_GERAL.error("Sem resultado de Importação. | Possível falha de importação.")

            self.interrupt_driver()
            return True
        except TimeoutException:
            self.interrupt_driver()
            raise DriverInterrupted("Erro ao aguardar tabela Resultado de Importação | Possível falha de importação.")

    # --> Aguada o resultado do INPUT.
    def wait_result(self):
        time_request = 0

        while True:
            try:
                loading_stage = self._longWait.until_not(EC.presence_of_element_located((By.CLASS_NAME, 'css.virk8d')))
                tabela_result = self._longWait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.css-0')))
                resultados = tabela_result.find_elements(By.CSS_SELECTOR, 'tr.css-0')[0]
                output = [x.text for x in WebDriverWait(resultados, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td.css-1haryci')))]

                if output[0].lower() == datetime.today().strftime('%d/%m/%Y') and output[2].lower() != "iniciado":
                    return output

                else:
                    sleep(1)
                    time_request += 1
                    if time_request > TEMPO_RESPOSTAS["wait_request"]:
                        return False
            except TimeoutException:
                self.interrupt_driver()
                raise DriverInterrupted("Erro ao aguardar tabela Resultado de Importação | Possível falha de importação.")
            
    def check_backdrop(self):
        try:
            self._midWait.until(EC.presence_of_element_located((By.CLASS_NAME, ('css-18soxw1'))))
            self.driver.execute_script('document.getElementsByClassName("css-18soxw1")[0].remove();')

        except TimeoutException:   
            return True
    
    def check_terms(self):
        try:
            self._midWait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-testid=\"Termos de Uso e Política de Privacidade.Title\"]')))
            self._midWait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-1n9f0ck')))
            self.driver.execute_script('document.getElementsByClassName("css-1n9f0ck")[0].remove();')
            button = self._shortWait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-7a0r74')))
            button.click()
            return True
        except TimeoutException:
            return True

    # --> Encerra o BOT.
    def interrupt_driver(self):
        LOG_GERAL.info(f"Finalizando Processo - URL: {self._host} | {self._municipio.upper()}")
        self.driver.quit()

if __name__ == '__main__':
    pass