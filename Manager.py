from bot import eASAgent, eSUSAgent
import os
import xml.etree.ElementTree as ET
import zipfile
from const import XML_PATH, PEC_IPS, LOG_GERAL, LOGS_PATH, LOG_ERROR, EAS_HOSTS, CONFIG
from datetime import datetime
from ExceptionClass import *
from data.dbsource import LocalStorage
from analytics import enviar_log

LOCAL_STORAGE = LocalStorage()

class XML_CNES:
    def __init__(self, file_xml) -> None:
        self._id = None
        self._exists = False
        self._dataXml = None
        self._co_Ibge = None
        self._eas_imported: bool = False
        self._esus_imported: bool = False
        self._xml = self.__open_xml(file_xml)
        
        self.__check_database()
        
    def authentication(self, co_ibge):
        if self._xml and co_ibge == self._co_Ibge:    
            return self._xml
        else:
            return False  

    def __open_xml(self, file_xml):

        tree = ET.parse(file_xml)
        root = tree.getroot()
        identificacao = root[0]
        self._dataXml = identificacao.get("DATA")

        if self.__auth_data(self._dataXml):
            self._co_Ibge = identificacao.get("CO_IBGE_MUN")
            return file_xml
        else:
            raise UnauthorizedXML('XML Ultrapassado.')
    
    def __auth_data(self, dataXml):
       
        data_formatada = datetime.strptime(dataXml, '%Y-%m-%d')
        data_atual = datetime.now()
        diferenca = (data_atual - data_formatada).days
        if diferenca > data_atual.weekday()+1:
            return False
        else:
            return True

    def __check_database(self):
        for row in LOCAL_STORAGE._cursor.execute('select id, data_xml, co_ibge, eas_imported, esus_imported from lotes_importados'):
                if  row[1] == self._dataXml and self._co_Ibge == row[2]:
                    self._exists = True
                    self._id = row[0]
                    self._eas_imported = row[3]
                    self._esus_imported = row[4]

                    if self._eas_imported and self._esus_imported:
                        raise UnauthorizedXML('XML já inserido anteriormente.')
     
class Manager:
    
    def __init__(self) -> None:
        self.xml_queue: list[XML_CNES] = []

    def searchXML(self):
        xml_path_list = os.listdir(XML_PATH)
        for cnes_xml_file in xml_path_list:
            try:
                try:
                    if cnes_xml_file.endswith('.ZIP') or  cnes_xml_file.endswith('.zip'):
                        with zipfile.ZipFile(os.path.join(XML_PATH, cnes_xml_file), 'r') as zipfile_xml_cnes:
                            with zipfile_xml_cnes.open(zipfile_xml_cnes.namelist()[0]) as unziped_xml_cnes:
                                xml = XML_CNES(unziped_xml_cnes)
                                self.xml_queue.append(xml)                        

                    elif cnes_xml_file.endswith('.xml'):
                        unziped_xml_cnes = os.path.join(XML_PATH, cnes_xml_file)
                        xml = XML_CNES(unziped_xml_cnes)
                        self.xml_queue.append(xml)
                        
                except zipfile.BadZipFile as e:
                    print("Apenas arquivos '.zip' ou '.xml'")    
            except UnauthorizedXML as e:
                continue
        if not self.xml_queue:
            LOG_GERAL.info("Sem XML's válidos para processamento na data e horário atual.")
            LOG_ERROR.info("Sem XML's válidos para processamento na data e horário atual.")
            return False
        else:
            return True

    def ImportInstructions(self) -> None:

        for estado, municipios in PEC_IPS.items():
            for municipio, dados in municipios.items():
                credenciais_pec = dados['CREDENCIAIS']
                credenciais_eas = CONFIG['CREDENCIAISRTG']

                xml: XML_CNES = self.__check_xml(dados['IBGE'])

                if xml:
                    if not xml._exists:
                        xml._id = self.__register_bd_lote(municipio, xml)

                    if not xml._eas_imported:
                        for cliente_retaguarda in EAS_HOSTS.values():
                            if municipio in cliente_retaguarda or f'{municipio.replace(' ', '')}{estado}' in cliente_retaguarda:
                                try: 
                                    AGENT_EAS = eASAgent.RetaguardaBOT((municipio.replace(' ', ''), estado), cliente_nome=municipio, carga=xml._xml)
                                    if self.__EASInstructions(AGENT_EAS, credenciais_eas, municipio):
                                        self.__register_bd_eas(municipio, xml, True)
                                        xml._eas_imported = True
                                        self.__register_bd_lote(municipio, xml)
                                    break
                                except DriverInterrupted as e:
                                    self.__register_bd_eas(municipio, xml, False)
                                    LOG_GERAL.error(f'{e} - RETAGUARDA: {municipio}')
                                    LOG_ERROR.error(f'{e} - RETAGUARDA: {municipio}')
                                    break           
                    
                    if not xml._esus_imported:
                        _only_absentess = self.__check_absentees(xml._id)
                        for unidade, ip in dados['IPS'].items():
                            if _only_absentess and unidade in _only_absentess:
                                continue

                            LOG_GERAL.info("")
                            try:
                                AGENT = eSUSAgent.eSUSBOT((ip, '8080'), cliente=(municipio, unidade), carga=xml._xml)
            
                                if self.__eSUSInstructions(AGENT, credenciais_pec, municipio):
                                    self.__register_bd_esus(municipio, unidade, xml, True)
                                    AGENT.result()
                                
                            except DriverInterrupted as e:
                                self.__register_bd_esus(municipio, unidade, xml, False)
                                LOG_GERAL.error(f'{e} - {municipio} - {unidade} - {ip}')
                                LOG_ERROR.error(f'{e} - {municipio} - {unidade} - {ip}')
                                continue
                    
                        if self.__check_esus_sucess == len(dados["IPS"]):
                            xml._esus_imported = True
                            self.__register_bd_lote(municipio, xml)

    def __eSUSInstructions(self, agent: eSUSAgent.eSUSBOT, credenciais:dict, municipio:str):
        try:
            _AUTH = agent.login(credenciais["user"], credenciais["password"])

            if _AUTH:
                agent.check_terms()
                if agent.select_profile(municipio, "administrador municipal"):
                    agent.check_backdrop()
                    if agent.goto('importarCnes'):
                        agent.check_backdrop()
                        _IMPORTACAO = agent.importar_xml()
                        if _IMPORTACAO: 
                            return True
            else:
                agent.interrupt_driver()
                raise DriverInterrupted('Login ou Senha Incorretos.')
        except Exception as e:
            raise DriverInterrupted(e)

    def __EASInstructions(self, agent: eASAgent.RetaguardaBOT, credenciais:dict, municipio:str):
        try:
            _AUTH = agent.login(credenciais['user'], credenciais['password'])

            if _AUTH:
                agent.goto('Prefeitura/ImportarXML')
                _IMPORTACAO = agent.importar_xml()
                if _IMPORTACAO:
                    return True
            else:
                raise DriverInterrupted('Login ou Senha Incorretos.')
        except Exception as e:
            raise DriverInterrupted(e)

    def __register_bd_lote (self, municipio:str, xml:XML_CNES):
        return LOCAL_STORAGE.insert_lote(municipio, xml._co_Ibge, xml._xml, xml._dataXml, datetime.today(), xml._eas_imported, xml._esus_imported)    

    def __register_bd_esus(self, municipio, unidade, xml, imported: bool):
        LOCAL_STORAGE.insert_esus(municipio, unidade, xml._co_Ibge, xml._xml, xml._dataXml, datetime.today(), xml._id, imported)       

    def __register_bd_eas(self, municipio: str, xml: XML_CNES, imported: bool):
        LOCAL_STORAGE.insert_eas(municipio, xml._co_Ibge, xml._xml, xml._dataXml, datetime.today(), xml._id, imported)       
    
    def __check_xml(self, ibge:str):
        
        xml_frequency_list = [] 

        for xml in self.xml_queue:
            if xml.authentication(ibge):
                xml_frequency_list.append(xml)
        
        if xml_frequency_list:
            last_xml: XML_CNES = max(xml_frequency_list, key=lambda xml_obj: xml_obj._dataXml)

            importados = LOCAL_STORAGE._cursor.execute('''select data_xml, municipio, co_ibge from lotes_importados where co_ibge = ?''',(ibge,))
            importados = importados.fetchall()

            if importados:
                last_DB_date = datetime.strptime(max(importados, key=lambda x: x[0])[0], '%Y-%m-%d')
                last_xml_date = datetime.strptime(last_xml._dataXml, '%Y-%m-%d')
                if last_DB_date > last_xml_date:
                    return None     
            return last_xml
        else:
            return None
    
    def __check_esus_sucess(self):
        sucess = LOCAL_STORAGE._cursor.execute('''select * from lotes_importados_esus where xml_reference = ? and imported = 1''', (id,)).fetchall()
        if sucess:
            return len(sucess)
        return None

    def __check_absentees(self, id):
        absentees = LOCAL_STORAGE._cursor.execute('''select * from lotes_importados_esus where xml_reference = ? and imported = 1''', (id,)).fetchall()
        if absentees:
            return [x[2] for x in absentees]
        return False

def check_log():
    for log in os.listdir(LOGS_PATH):
        if datetime.today().strftime("%d-%m-%Y") in log:
            with open(os.path.join(LOGS_PATH, log), "w") as log_file:
                log_file.write("")
                log_file.close()                    

if __name__ == '__main__':
    check_log()
    manager = Manager()

    #Carregar XML´s de possível inserção na pasta.
    if manager.searchXML():
        manager.ImportInstructions()
        enviar_log()
    
    