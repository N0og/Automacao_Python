import sqlite3

class LocalStorage:
    def __init__(self) -> None:     
        self._conn = sqlite3.connect('data/imported.db')
        self._cursor = self.cursor()

    def cursor(self) -> sqlite3.Cursor:
        return self._conn.cursor()
    
    def insert_lote(self, *params):
        id = None

        municipio, co_ibge, file_url, data_Xml = params[:4]

        incidencia = self._cursor.execute('''select id from lotes_importados where municipio = ? and co_ibge = ? and data_xml = ?''', (municipio, co_ibge, data_Xml))
        id = incidencia.fetchone()

        if id:
            self._cursor.execute('''update lotes_importados set 
                                    eas_imported = ?,
                                    esus_imported = ?
                                    where id = ?
                                ''', (params[5], params[6], id[0]))

        else:
            insercao = self._cursor.execute('''insert into lotes_importados (municipio, co_ibge, file_url, data_xml, data_importado, eas_imported, esus_imported)
                                    values(?,?,?,?,?,?,?)
                                    ''', (params))
            
            id = (insercao.lastrowid,)
            
        self._conn.commit() 
        return id[0]
        

    def insert_eas(self, *params):

        municipio, co_ibge, file_url, data_Xml = params[:4]

        incidencia = self._cursor.execute('''select id from lotes_importados_eas where municipio = ? and co_ibge = ? and data_xml = ?''', 
                                          (municipio, co_ibge, data_Xml))
        result = incidencia.fetchall()
        if result:
            self._cursor.execute('''update lotes_importados_eas set 
                                    imported = ?
                                    where id = ?
                                ''', (params[6], result[0][0]))

        else:
            self._cursor.execute('''insert into lotes_importados_eas (municipio, co_ibge, file_url, data_xml, data_importado, xml_reference, imported)
                                        values(?,?,?,?,?,?,?)
                                        ''', (params))
        self._conn.commit()
    
    def insert_esus(self, *params):
        municipio, unidade, co_ibge, file_url, data_Xml = params[:5]

        incidencia = self._cursor.execute('''select id from lotes_importados_esus where municipio = ? and unidade = ? and co_ibge = ? and data_xml = ?''',
                                           (municipio, unidade, co_ibge, data_Xml))
        result = incidencia.fetchall()
        if result:
            self._cursor.execute('''update lotes_importados_esus set 
                                    imported = ?
                                    where id = ?
                                ''', (params[7], result[0][0]))

        else:
            self._cursor.execute('''insert into lotes_importados_esus (municipio, unidade, co_ibge, file_url, data_xml, data_importado, xml_reference, imported)
                                        values(?,?,?,?,?,?,?,?)
                                        ''', (params))
        self._conn.commit()
    

    def create_base(self):

        self._cursor.execute('''
                             create table lotes_importados (
                                id integer primary key,
                                municipio text,
                                co_ibge text,
                                file_url text,
                                data_xml date,
                                data_importado date,
                                eas_imported bool,         
                                esus_imported bool
                             ) ''')
        

        self._cursor.execute('''
                             create table lotes_importados_eas (
                                id integer primary key,
                                municipio text,
                                co_ibge text,
                                file_url text,
                                data_xml date,
                                data_importado date,
                                xml_reference integer,
                                imported bool,
                                foreign key (xml_reference) references lotes_importados(id)
                             ) ''')
        
        self._cursor.execute('''
                             create table lotes_importados_esus (
                                id integer primary key,
                                municipio text,
                                unidade text,
                                co_ibge text,
                                file_url text,
                                data_xml date,
                                data_importado date,
                                xml_reference integer,
                                imported bool,
                                foreign key (xml_reference) references lotes_importados(id)
                             ) ''')
        
        self._conn.commit()

    
if __name__ == '__main__':
    LocalStorage().create_base()
    
