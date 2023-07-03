from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils import add_custom_index_cell
from utils import write_to_csv
from mail_sender import MailSender
from utils import get_final_report
from utils import get_data_with_selenium

if __name__ == "__main__":
    service = Service(executable_path='Users\gabri\crypto-scraper\chromedriver_win32')
    with webdriver.Chrome(service=service) as driver:
        driver.get('https://coinmarketcap.com')

        table = []
        PAGES_TO_SCRAPE = 3
        for page in range(1, PAGES_TO_SCRAPE + 1):
            get_data_with_selenium(driver=driver, table=table)

    add_custom_index_cell(table)
    print(get_final_report(table))
    write_to_csv(table)

    crypto_mail = MailSender(
        mail_server='smtp.gmail.com',
        port=465,
        sender='email@teste.com',
        receiver='email@teste.com',
        subject=f'Dados cripto com arquivo',
        body_msg=get_final_report(table),
        attachment_file_path='crypto_data.csv'
    )

    crypto_mail.send_mail()
