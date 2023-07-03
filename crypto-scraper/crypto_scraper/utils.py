import time
import csv
from selenium.webdriver.common.by import By


def get_tag_percentage_value(tag):
    """
    Processa o objeto Tag de um <td> que armazena a variação percentual de uma criptomoeda.
    :param tag: Objeto beautifulsoup Tag
    :return: Retorna um valor float, com 2 casas decimais e com sinal positivo ou negativo.
    """
    percentage_delta = round(float(tag.text.strip("%")), 2)

    if "down" in tag.span.get("class")[0]:
        percentage_delta = percentage_delta * -1

    return percentage_delta + 0


def get_web_element_percentage_value(we):
    """
    Processa o objeto WebElement de uma tag HTML <td> que armazena a variação
    percentual de uma criptomoeda.
    :param we: Objeto selenium WebElement
    :return: Retorna um valor float, com 2 casas decimais e com sinal positivo
    ou negativo.
    """
    percentage_delta = round(float(we.text.strip("%")), 2)

    if "down" in we.find_element(By.XPATH, ".//span/span").get_attribute("class"):
        percentage_delta = percentage_delta * -1

    return percentage_delta + 0


def sort_by_field(table, field, reverse=True):
    """
    Retorna uma cópia da lista 'table', porém com os dicionários internos ordenados
    com base no valor associado a chave 'field'. Se Reverse for 'True', a ordenação
    é descendente. Caso contrário, ascendente.
    :param table: uma lista de dicionários representando a tabela de criptomoedas.
    Cada dicionário contém 12 pares chave-valor, representando cada uma das 12 colunas
    de interesse em uma linha.
    :param field: uma string com o nome da chave que representa a coluna da tabela a ser
    usada como parâmetro de ordenação.
    :param reverse: Boolean que determina se a ordenação de ser feita do maior para o
    menor, ou o contrário.
    :return: uma cópia da lista 'table' com os elementos ordenados conforme os
    parâmetro acima.
    """

    def _select_field(row):
        return row[field]

    return sorted(table, key=_select_field, reverse=reverse)


def get_money_as_number(money_str, number_type=float):
    """Converte a string 'money_str para um numero do tipo 'number_type"""
    return number_type(money_str.lstrip("$").replace(",", "").replace(".", ""))


def get_custom_index(coin_data):
    """
    Obtem o indice definido por:
        -MARKET CAP * %valorização em 7 dias/ Preço
    :param coin_data: um dicionario contendo todos os dados sobre a criptomoeda
    :return: Um numero float com duas casas decimais
    """
    market_cap = get_money_as_number(money_str=coin_data["market_cap"])
    perc_delta = coin_data["one_week"]
    price = get_money_as_number(money_str=coin_data["price"])

    return (market_cap * perc_delta) / price


def add_custom_index_cell(table):
    """
    Adiciona mais um par chave-valor a cada dicionario dentro da lista
    'table', sendo a chave 'custom_index', e o valor, o retorno da função
    get_custom_index para a cripto em questao
    :param table: uma lista de dicionarios, com cada dicionario contendo
    dados relativos a uma criptomoeda
    """
    for row in table:
        row["custom_index"] = round(get_custom_index(row), 2)


def write_to_csv(table):
    with open("crypto_data.csv", mode="w") as csv_file:
        headers = table[0].keys()
        csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
        csv_writer.writeheader()

        for row in table:
            csv_writer.writerow(row)


def get_line_in_section(line_prefix, coin_data, report_fields):
    """
        Processa 1 linha dentro de uma sessão do relatório final que deve ser
        apresentado ao usuário
        :param line_prefix: string que deve aparecer no começo da linha.
        :param coin_data: dicionário que representa 1 cripto moeda
        :param report_fields: os campos do dicionário 'coin_data' que devem
        constar na linha.
        """
    fields_data = []
    for k, v in coin_data.items():
        if k in report_fields:
            fields_data.append(str(v))

    line_data = " - ".join(fields_data)
    return f"\t{line_prefix} {line_data}"


def get_appreciation_section(table, report_fields, header, reverse=True):
    """
    Monta a sessão do relatório referente a valorização das moedas para os
    períodos de 1hr, 1dia, 1semana
    """
    last_hr_coin = sort_by_field(table=table, field='one_hr', reverse=reverse)[0]
    last_hr_line = get_line_in_section("na última hora:", last_hr_coin, report_fields)

    last_day_coin = sort_by_field(table=table, field='one_day', reverse=reverse)[0]
    last_day_line = get_line_in_section("no último dia:", last_day_coin, report_fields)

    last_week_coin = sort_by_field(table=table, field='one_week', reverse=reverse)[0]
    last_week_line = get_line_in_section("na última semana:", last_week_coin, report_fields)

    session = (
        f"{header}\n"
        f"{last_hr_line}\n"
        f"{last_day_line}\n"
        f"{last_week_line}\n"
    )

    return session


def get_custom_index_section(table, report_fields, header):
    """
    Monta a sessão do relatório referente ao Custom Index
    """
    top_coins = sort_by_field(table=table, field='custom_index')[:10]
    report_lines = [get_line_in_section('', coin, report_fields) for coin in top_coins]

    session = "{}\n{}".format(header, '\n'.join(report_lines))

    return session


def get_final_report(table):
    """
    Modanta um relatorio final para o usuario
    :param table: uma lista contendo todas as linhas lidas da pagina
    HTML
    """
    top_aprreciated_coins_report = get_appreciation_section(
        table,
        ['name', 'one_hr', 'one_day', 'one_week'],
        "A criptomoeda que mais valorizou:"
    )

    least_appreciated_coins_report = get_appreciation_section(
        table,
        ['name', 'one_hr', 'one_day', 'one_week'],
        "A criptomoeda que mais desvalorizou:",
        reverse=False
    )

    custom_index_report = get_custom_index_section(
        table,
        ['name', 'price', 'custom_index'],
        "Top 10 de acordo com o Custom Index:"
    )

    final_report = "Resumo\n" + "\n".join(
        [top_aprreciated_coins_report, least_appreciated_coins_report, custom_index_report])

    return final_report


def scroll_page(driver):
    """
    Garante que a página será totalmente scrolled para a ultima posicao possivel.
    :param driver: um Webdriver Selenium
    """
    height = driver.execute_script("return document.body.scrollHeight")
    scroll = 0
    while True:
        scroll += 1
        driver.execute_script(f"window.scrollTo(0,{1080 * scroll})")
        if scroll * 1080 >= height:
            break
        time.sleep(1)


def scrape_relevant_data(driver, table):
    """
    Contem a lógica de scraping necessária para obter os dados das 12 células de
    interesse em cada linha da tabela.
    :param driver: um Webdriver Selenium
    :param table: uma lista que armazena os dados obtidos via scraping em dicionários
    python
    """
    crypto_rows = driver.find_elements(By.XPATH, '//tbody/tr')
    for tr in crypto_rows:
        _, _, name, price, one_hr, one_day, one_week, market_cap, volume, circ_supply, \
            weekly_chart, _ = tr.find_elements(By.XPATH, ".//td")
        processed_row = {
            'name': name.text.split("\n")[0],
            'price': price.text,
            'one_hr': get_web_element_percentage_value(one_hr),
            'one_day': get_web_element_percentage_value(one_day),
            'one_week': get_web_element_percentage_value(one_week),
            'market_cap': market_cap.text,
            'volume': volume.text.split("\n")[0],
            'circ_supply': circ_supply.text.split(" ")[0],
            'week': weekly_chart.find_element(By.TAG_NAME, "a").get_attribute("href")
        }
        table.append(processed_row)


def click_next_page(driver):
    """
    clica no link que leva para uma próxima página.
    :param driver: um Webdriver Selenium
    """
    next_page_link = driver.find_element(By.XPATH, '//li/a[@aria-label="Next page"]')
    driver.execute_script("arguments[0].click();", next_page_link)


def get_data_with_selenium(driver, table):
    """
    Concentra toda a logica de manipulacao do navegador e de scraping
    :param driver: um Webdriver Selenium
    :param table: uma lista que armazena os dados obtidos via scraping em dicionários
    """
    scroll_page(driver=driver)
    scrape_relevant_data(driver=driver, table=table)
    click_next_page(driver=driver)
