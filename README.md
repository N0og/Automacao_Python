<h1>Automacao_Python</h1> 

 Automação baseada no Selenium WebDriver utilizando Python, responsável pela inserção de dados do Cadastro Nacional de Estabelecimentos de Saúde (CNES) nas plataformas dependentes eSUS AB (PEC) e AtendSaúde.


## OBJETIVO

    Considerando a necessidade de implementar um processo automático para a importação dos arquivos .xml disponibilizados pelos municípios, a fim de atualizar os dados de estabelecimentos e vínculos das plataformas eSUS AB e AtendSaúde, foi desenvolvida uma solução automatizada para realizar e monitorar esta função. O projeto traz melhorias significativas no fluxo de inserção desses dados, devido ao uso de um fluxo algorítmico que aborda diversas possibilidades, tratando os obstáculos de forma a serem notificados e resolvidos automaticamente durante suas execuções.

## ARQUITETURA

    O software está dividido em um Gerenciador, dois BOTs de execução e uma abstração de banco de dados local. O objetivo do Gerenciador é organizar a ordem de execução dos passos e estabelecer normas e critérios a serem cumpridos para que um BOT seja instanciado. Ele é responsável por garantir que arquivos indesejados, antigos ou fora de conformidade não entrem na lista de importação. O banco de dados serve como fonte histórica dos dados já processados, mantendo informações sobre as referências do XML, a data da tentativa de importação e se o processo foi concluído com sucesso ou não para cada arquivo.

    Os BOTs são os manipuladores diretos das plataformas que recebem os dados do CNES. Eles garantem que o arquivo seja devidamente enviado para o input de cada plataforma e que o resultado do processo seja captado de acordo com seu sucesso ou suas exceções. Os BOTs estão limitados à ação e ao relatório, não sendo responsáveis por determinar o que é ou não é devido para o processo.

## RECURSOS COMPUTACIONAIS

    Com o objetivo de economizar processamento e memória, todas as verificações que eliminam a necessidade de processamento ocorrem logo no início da execução do software. No entanto, durante a execução, utiliza-se um webdriver baseado no Chrome ou Edge, que são réplicas dos navegadores de uso pessoal, consumindo recursos de memória de forma semelhante a estes. É importante ressaltar que o processo ocorre de forma sequencial, não havendo concorrência ou pseudoparalelismo dos serviços dos BOTs. Portanto, o consumo de memória é reservado de acordo com o webdriver em execução.


## CRITÉRIOS DE VALIDAÇÃO DO XML CNES

    1. Formato do Arquivo:
    ● O arquivo deve estar no formato padrão '.xml' ou '.zip', contendo o XML compactado.

    2. Data do XML:
    ● A data do XML deve corresponder à semana vigente.

    3. Registro no Banco de Dados:
    ● O XML não deve possuir registro no banco de dados. No entanto, caso exista, serão verificadas as flags de importação para as plataformas receptoras (AtendSaúde e eSUS AB). Se uma destas flags estiver com valor falso, o XML será considerado novamente para processamento apenas das unidades ou plataformas faltantes.

    4. Código do IBGE:
    ● O código do IBGE presente no arquivo '.xml' deve ser idêntico ao código IBGE do município destinatário do conteúdo.

    5. Prioridade de XMLs para o Mesmo Município:
    ● Se houver mais de um XML do mesmo município com data válida para inserção, será considerado apenas o XML com a data mais próxima ou igual à data atual do processamento.

    6. Avaliação de Prioridade para XMLs: Desconsideração em Caso de Dados Mais Atualizado:
    ● Se existir um registro no banco de dados de um XML com data superior àquela selecionada para processamento, o selecionado será desconsiderado, visto que já houve a importação de um dado mais atualizado.