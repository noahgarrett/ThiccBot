import requests
from bs4 import BeautifulSoup

AAPL_url = 'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch'

response = requests.get(AAPL_url)
soup = BeautifulSoup(response.text, 'lxml')

price = soup.find_all('div', {'class':'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
print(price)

stock_urls = {
        "AAPL": 'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch',
        "AMZN": 'https://finance.yahoo.com/quote/AMZN?p=AMZN&.tsrc=fin-srch'
    }
for key, value in stock_urls.items():
    print(key, value)

