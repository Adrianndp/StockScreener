import requests
import pandas as pd
from io import StringIO


def get_sp500_tickers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url, headers=headers)
    html = response.text
    sp500 = pd.read_html(StringIO(html))[0]
    sp500["Symbol"] = sp500["Symbol"].str.replace(".", "-", regex=False)
    sp_tickers = sp500['Symbol'].tolist()
    sp_tickers = sorted(sp_tickers)
    return sp_tickers
