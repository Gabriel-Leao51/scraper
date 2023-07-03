from bs4 import BeautifulSoup
import requests
from utils import get_tag_percentage_value
from utils import sort_by_field

url = "https://coinmarketcap.com"
web_page = requests.get(url)
html_document = web_page.text
soup = BeautifulSoup(html_document, "html.parser")

crypto_table_body = soup.tbody

table = []
for tr in crypto_table_body.contents:
    try:
        _, _, name, price, one_hr, one_day, one_week, market_cap, volume, circ_supply, weekly_chart, _ = tr.contents
    except ValueError:
        break
    processed_row={
        'name': name.p.text,
        'price': price.span.text,
        'one_hr': get_tag_percentage_value(tag=one_hr.span),
        'one_day': get_tag_percentage_value(tag=one_day.span),
        'one_week': get_tag_percentage_value(tag=one_week.span),
        'market_cap': market_cap.find(name="span", attrs={"data-nosnippet":"true"}).text,
        'volume': volume.p.text,
        'circ_supply': circ_supply.p.text,
        'weekly_chart': f"{url}{weekly_chart.a.get('href')}"
    }
    table.append(processed_row)

for row in table:
    print(row)

print("A criptomoeda que mais valorizou: ")
print(f"\t na última hora:{sort_by_field(table=table, field='one_hr')[0]}")
print(f"\t no último dia:{sort_by_field(table=table, field='one_day')[0]}")
print(f"\t na última semana:{sort_by_field(table=table, field='one_week')[0]}")

print("A criptomoeda que mais desvalorizou: ")
print(f"\t na última hora:{sort_by_field(table=table, field='one_hr', reverse=False)[0]}")
print(f"\t no último dia:{sort_by_field(table=table, field='one_day', reverse=False)[0]}")
print(f"\t na última semana:{sort_by_field(table=table, field='one_week', reverse=False)[0]}")