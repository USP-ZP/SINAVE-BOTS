import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import yaml
from yaml.loader import SafeLoader
import logging


def login_and_filter(browser: webdriver, wait: WebDriverWait, credenciais):
    # credenciais
    username = credenciais.get('username')
    password = credenciais.get('password')

    # Login
    browser.get('https://sinave.min-saude.pt/SINAVE.MIN-SAUDE/login.html')
    browser.find_element(By.NAME, 'username').send_keys(username)
    browser.find_element(By.NAME, 'password').send_keys(password)
    browser.find_element(By.XPATH, '//form//input[@type="submit"]').click()

    time.sleep(1)

    try:
        # click Saúde Pública Button
        img = browser.find_element(By.ID, 'autsaudimg')
        browser.find_element(By.ID, 'autsaudimg').click()
    except NoSuchElementException:
        print("short login")

    # wait for page to load
    wait.until(EC.presence_of_element_located((By.ID, 'tipo_ent')))
    # select Entidade Associada
    select = Select(browser.find_element(By.ID, 'tipo_ent'))
    select.select_by_index(1)
    # Click proceed
    browser.find_element(By.XPATH, '//form[@id="formChooseInstitut"]/div/footer/button[1]').click()

    # wait for page to load
    wait.until(EC.presence_of_element_located((By.ID, 'notif')))
    # browser.find_element(By.LINK_TEXT, "Listar Notif. Clínicas")
    # click notificações
    # browser.find_element(By.LINK_TEXT, "Listar Notif. Clínicas")
    browser.find_element(By.ID, 'notif').click()

    # wait for page to load
    wait.until(EC.presence_of_element_located((By.ID, 'id_doenca')))

    # Select SARS-CoV-2 in doenças
    doenca_ele = browser.find_element(By.ID, 'id_doenca_chosen')
    doenca_ele.click()
    doenca_ele.find_element(By.TAG_NAME, 'INPUT').send_keys('Infeção pelo SARS-CoV-2/COVID-19')
    doenca_ele.find_element(By.TAG_NAME, 'INPUT').send_keys(Keys.ENTER)

    # estado notificacao
    select = Select(browser.find_element(By.ID, 'estado_notificacao'))
    select.select_by_visible_text('Aguarda IE')

    # concelho
    select = Select(browser.find_element(By.ID, 'id_concelho'))
    select.select_by_visible_text('Caldas da Rainha')

    # submit
    browser.find_element(By.ID, 'btPesq').click()

    # wait for page to load
    wait.until(EC.presence_of_element_located((By.ID, 'orderSelect')))


def ordenar_resultados(browser: webdriver):
    # order results
    select = Select(browser.find_element(By.ID, 'orderSelect'))
    select.select_by_visible_text('Número de Notificação: Crescente')


def obter_info_caso(browser: webdriver, wait: WebDriverWait) -> dict:
    row = browser.find_element(By.XPATH, '//table[@id="example2"]/tbody/tr')
    return {
        "num_notificacao": row.find_elements(By.TAG_NAME, 'td')[1].text,
        "data_notificacao": row.find_elements(By.TAG_NAME, 'td')[3].text,
        "num_utente": row.find_elements(By.TAG_NAME, 'td')[5].text
    }


def criar_caso(browser: webdriver, wait: WebDriverWait, info):
    browser.find_element(
        By.XPATH,
        '//table[@id="example2"]/tbody/tr/td/button[last()][contains(@title, "Criar Caso")]').click()

    wait.until(EC.presence_of_element_located((By.ID, 'formCase')))

    browser.find_element(
        By.XPATH,
        "//*[@id='formCase']/div//button[contains(@title, 'Gravar Caso')]").click()


def preencher_ie(browser: webdriver, wait: WebDriverWait):
    wait.until(EC.presence_of_element_located((By.ID, '19354_11429_8_103579_10_19355_4283')))

    infecao_ncov = browser.find_element(By.ID, '19354_11429_8_103579_10_19355_4283')

    # verificar se é prof saúde
    try:
        if browser.find_element(By.ID, '19373_11443_8_103631_10_Y').is_selected():
            select_ps = Select(browser.find_element(By.ID, 'list_20151_11615_11443_104190_10'))
            select_ps.select_by_visible_text('Outro')
    except NoSuchElementException:
        print('skip prof saude')

    if not infecao_ncov.is_selected():
        infecao_ncov.click()

    # descobrir se é sintomatico
    is_sintomatico = False
    ids_campos_sintomas = [
        '19535_11502_8_103725_10_Y',
        '13518_9998_8_103727_10_Y',
        '13481_9973_8_103585_10_Y',
        '19471_11470_8_103678_10_Y',
        '13576_10039_8_103586_10_Y',
        '19359_11431_8_103587_10_Y',
        '15157_10658_8_103588_10_Y',
        '15143_10645_8_103679_10_Y',
        '6394_5620_8_103680_10_Y',
        '15138_10640_8_103589_10_Y',
        '19537_11504_8_103728_10_Y',
        '15151_10652_8_103591_10_Y',
        '20177_11626_8_104203_10_Y',
        '20178_11627_8_104204_10_Y',
        '19475_11474_8_103685_10_Y',
        '19477_11476_8_103687_10_Y',
        '19461_11467_8_103676_10_19459_1237',
        '19469_11469_8_103677_10_19467_1237',
        '19364_11434_8_103596_10_19362_4285',
        '19364_11434_8_103596_10_19363_4286'
    ]

    classificacao = "Desconhecido"
    is_criterios_imagem = None
    is_criterios_epidemio = False

    # primeiro vemos se a checkbox está selecionada
    sintomatico = browser.find_element(By.ID, '19290_11402_8_103723_10_19289_4272')

    if sintomatico.is_selected():
        is_sintomatico = True
    else:
        for c_id in ids_campos_sintomas:
            if browser.find_element(By.ID, c_id).is_selected():
                is_sintomatico = True
                break

    if browser.find_element(By.ID, '19477_11476_8_103687_10_Y').is_selected():
        is_criterios_imagem = True
    elif browser.find_element(By.ID, '19477_11476_8_103687_10_N').is_selected():
        is_criterios_imagem = False
    else:
        is_criterios_imagem = None

    ########################################################
    # Criterios Laboratoriais
    is_criterios_lab = False
    select1 = Select(browser.find_element(By.ID, 'list_19393_11447_7597_103638_10'))
    select2 = Select(browser.find_element(By.ID, 'list_19377_11445_7597_103633_10'))  # mers-COV
    sinave_lab = browser.find_element(By.ID, 'example3').find_elements(By.XPATH, './*')
    num_nots_lab = len(sinave_lab)

    # tem teste rapido positivo
    if browser.find_element(By.ID, '19050_11313_8_104215_10_19051_1256').is_selected():
        is_criterios_lab = True
    elif select1.first_selected_option.text == 'Positivo':
        is_criterios_lab = True
    elif select2.first_selected_option.text == 'Positivo':
        is_criterios_lab = True
    # elif browser.find_element(By.ID, '8703_7597_8_102913_10_N').is_selected() or not browser.find_element(By.ID, '8703_7597_8_102913_10_Y').is_selected():
    #    is_criterios_lab = False
    # elif num_nots_lab == 0:
    #    is_criterios_lab = False

    if is_sintomatico:
        if not browser.find_element(By.ID, '15837_10988_9_999902_11_15837_1237').is_selected():
            browser.find_element(By.ID, '15837_10988_9_999902_11_15837_1237').click()
    else:
        if not browser.find_element(By.ID, '15837_10988_9_999902_11_15838_1234').is_selected():
            browser.find_element(By.ID, '15837_10988_9_999902_11_15838_1234').click()

    if is_criterios_imagem:
        if not browser.find_element(By.ID, '20199_11636_9_104213_11_Y').is_selected():
            browser.find_element(By.ID, '20199_11636_9_104213_11_Y').click()
    elif is_criterios_imagem is None:
        if not browser.find_element(By.ID, '20199_11636_9_104213_11_U').is_selected():
            browser.find_element(By.ID, '20199_11636_9_104213_11_U').click()
    else:
        if not browser.find_element(By.ID, '20199_11636_9_104213_11_N').is_selected():
            browser.find_element(By.ID, '20199_11636_9_104213_11_N').click()

    select_caso = Select(browser.find_element(By.ID, 'list_18990_11298_9_103675_11'))
    if is_criterios_lab:
        select_caso.select_by_visible_text('Confirmado')
        classificacao = "Caso Confirmado"
    elif (is_sintomatico and is_criterios_imagem) or (is_sintomatico and is_criterios_epidemio):
        select_caso.select_by_visible_text('Provável')
        classificacao = "Caso Provável"
    elif is_sintomatico:
        select_caso.select_by_visible_text('Possível')
        classificacao = "Caso Possível"
    else:
        select_caso.select_by_visible_text('Não é caso')
        classificacao = "Não é caso"

    browser.find_element(By.ID, 'saveBtn').click()
    return classificacao


def enviar_ie(browser: webdriver, wait: WebDriverWait, classificacao):
    wait.until(EC.presence_of_element_located((By.ID, 'caseStatusSelect')))
    select = Select(browser.find_element(By.ID, 'caseStatusSelect'))
    select.select_by_visible_text(classificacao)
    x_path = '//*[@id="formCase"]/div//button[contains(@title, "Validar o Caso e enviar para DSP")]'
    browser.find_element(By.XPATH, x_path).click()
    time.sleep(1)
    # x_path2 = '//div[@class="modal"]//button[contains(@data-bb-handler, "confirm")]'
    x_path2 = '/html/body/div[2]/div/div/div[2]/button[2]'
    browser.find_element(By.XPATH, x_path2).click()


def validate_config(cfg: dict):
    credenciais = cfg.get('credenciais')
    if credenciais is None:
        raise Exception('O ficheiro de configuração está mal formado: não contem credenciais')

    if credenciais.get('username') is None:
        raise Exception('O ficheiro de configuração está mal formado: as credenciais não contém username')

    if credenciais.get('password') is None:
        raise Exception('O ficheiro de configuração está mal formado: as credenciais não contém password')

    logs = cfg.get('logs')

    if logs.get('filename') is None:
        cfg['logs']['filename'] = './logs.log'

    if logs.get('filemode') is None:
        cfg['logs']['filemode'] = 'w'

    mode = logs.get('filemode')

    if mode != 'w' and mode != 'a':
        raise Exception('O ficheiro de configuração está mal formado: filemode só pode ser `w` ou `a`')

    return cfg


def main():
    with open('config.yaml') as f:
        cfg = yaml.load(f, Loader=SafeLoader)
        cfg = validate_config(cfg)

    logging.basicConfig(
        filename=cfg['logs']['filename'],
        filemode=cfg['logs']['filemode'],
        encoding='utf-8',
        level=logging.INFO)

    opts = Options()
    # opts.add_experimental_option("debuggerAddress", "localhost:9222")
    # browser = webdriver.Firefox()
    browser = webdriver.Chrome(options=opts)
    browser.implicitly_wait(2)
    wait = WebDriverWait(browser, 30)

    login_and_filter(browser, wait, cfg.get('credenciais'))

    # CASOS LOOP
    for x in range(1000):
        try:
            ordenar_resultados(browser)
            time.sleep(4)

            # obter info
            info = obter_info_caso(browser, wait)

            # criar caso
            criar_caso(browser, wait, info)

            classificacao = preencher_ie(browser, wait)
            enviar_ie(browser, wait, classificacao)
            now = datetime.now()
            logging.info(f"[{now.strftime('%d/%m/%Y %H:%M:%S')}] notificação {info.get('num_notificacao')} de {info.get('data_notificacao')}")
            print(f"[{x}] {now.strftime('%d/%m/%Y %H:%M:%S')}  notificação {info.get('num_notificacao')} de {info.get('data_notificacao')}")

        except NoSuchElementException as e:
            logging.error(e)
            print(f"[{x}] ERROR!!!!", e)

        time.sleep(2)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
