import pandas as pd
import datetime as dt
from fetch_data import get_sp500_tickers
import yfinance as yf

tickers = get_sp500_tickers()
start = dt.datetime.now() - dt.timedelta(days=365)
end = dt.datetime.now()

stock = yf.Ticker('^GSPC')
data = stock.history(interval='1d', start=start, end=end)
print(data.head())

