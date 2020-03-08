import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver as wb
from time import sleep
import csv
import re
import pickle  # para gravar o dicionario com um objeto e manter sua estrutura
""" nao utilizados 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
"""

url = "http://sti.sites.unifesp.br/consulta-departamento"
browser = wb.Chrome()
browser.get(url)
texto = []
id_h3 = []
lista_docente = []
nome_arquivo = 'planilha.csv'

div_principal = browser.find_element_by_xpath('//*[@id="sp-component"]/div/div[2]')
count_h3 = len(div_principal.find_elements_by_xpath('./h3'))

text_h3 = div_principal.find_elements_by_tag_name('h3')
for item in text_h3:
    texto.append(item.text)
texto = list(filter(None, texto))  # para tirar os elementos vazios da lista

for i in range(1, 114, 2):  # os IDs das tags H3 são ímpares, por isso uma lista para ser usada com índice dos elementos
    id_h3.append(i)

i = 0
docent_index = 116

while i < count_h3:
    print(i)
    print(texto[i])
    id_t = "ui-id-" + str(id_h3[i])
    elemento = div_principal.find_element_by_id(id_t)
    elemento.click()
    sleep(2)
    try:

        id_h3_docente = str('//*[@id=') + str('"') + str('ui-id-') + str(docent_index) + str('"]')
        # import pdb;pdb.set_trace()
        sleep(2)
        print(id_h3_docente)
        div_cap = div_principal.find_element_by_xpath(id_h3_docente)
        sleep(1)
        div_cap.click()
        sleep(2)
        # para percorrer as divs internas
        loop = i + 1
        string_local = '/html/body/div[1]/div/section[7]/div/div/div/div/div[2]/div[' + str(loop) + ']/div[2]'
        div_docente = div_principal.find_element_by_xpath(string_local)
        docentes = div_docente.find_elements_by_tag_name('a')
        dict_temp = {} # dict temporario usado dentro do for para armazenar os dados de cada docente

        for nome in docentes:
            nome_prof = nome.text
            link_prof = nome.get_attribute('href')

            """
            EXEMPLO:
            Tipo: PROFESSOR ADJUNTO-A DEDICAÇÃO EXCLUSIVA
            Titulação: DOUTORADO
            Campus: SÃO PAULO
            Departamento: DEPARTAMENTO BIOFISICA
            """

            # regex para uniformizar os links e filtrar apenas informações dos docentes
            x = re.search(r"informacoes-do-docente", link_prof)
            pg = ''
            if x:
                print(nome_prof)
                print(link_prof)
                pg = requests.get(link_prof)

                if pg.status_code == 200:
                    soup = bs(pg.content, 'lxml')
                    div_conteudo = soup.find("div", id="sp-component") # div que contem as informações dos docentes

                    nome_docente = div_conteudo.find('h3').text
                    # div conteudo, retorna uma lista com as informações, como são as mesmas, é só acessar seu índice
                    text_tipo = div_conteudo.contents[5]
                    tipo = text_tipo.split(':')[1].strip()

                    text_titulacao = div_conteudo.contents[7]
                    titulacao = text_titulacao.split(':')[1].strip()

                    text_campus = div_conteudo.contents[9]
                    campus = text_campus.split(':')[1].strip()

                    dict_temp = {'Departamento': texto[i], 'Nome': nome_docente, 'Tipo': tipo, 'Titulação': titulacao,
                                 'Campus': campus}
                    lista_docente.append(dict_temp)

                elif pg.status_code == 404:
                    print('Não encontrado.')

        #print(lista_docente)
        print('----|||--------|||--------|||-----')
        print(f"FIM DA GRAVACAO Do departamento ----> {texto[i]}")

        #import pdb;pdb.set_trace()
        print("proximo departamento")
        print('\/\/\/\/\/\/\/\/\/\/\/\/\\')

    except Exception as e:
        print("Não carregou...", e)

    i += 1
    docent_index += 3 # o id começa em 116 e vai de 3 em 3 

# ----------------------- salvando a lista em .csv ---------------------------
arq = open('teste.txt', 'wb')
pickle.dump(lista_docente, arq)  # Grava uma stream do objeto "dic" para o arquivo.
arq.close()
# para ler o arquivo
# arq = open('teste.txt', 'rb')
# dic = pickle.load(arq)  # Ler a stream a partir do arquivo e reconstroi o objeto original.
# arq.close()
# print(dic)

# --------------------- gravando os dados em csv -------------------------------

variaveis = ['Departamento', 'Nome', 'Tipo', 'Titulação', 'Campus']

# função para gravar um csv linha a linha usando um dicionario
def grava_csv_linha_a_linha(nome_arquivo, lista_de_dict, nomes_variaveis):
    # Open file in append mode
    with open(nome_arquivo, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        dict_writer = csv.DictWriter(write_obj, fieldnames=nomes_variaveis)
        dict_writer.writeheader()
        # Add dictionary as wor in the csv
        for dados_docente in lista_de_dict:
            dict_writer.writerow(dados_docente)


grava_csv_linha_a_linha(nome_arquivo, lista_docente, variaveis)
