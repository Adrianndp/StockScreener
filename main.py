import pandas as pd
import datetime as dt
from fetch_data import get_sp500_tickers
import yfinance as yf

tickers = get_sp500_tickers()
start = dt.datetime.now() - dt.timedelta(days=365)
end = dt.datetime.now()

stock = yf.Ticker('^GSPC')
sp500_df = stock.history(interval='1d', start=start, end=end)
sp500_df['Pct Change'] = sp500_df['Close'].pct_change()
sp500_df['Pct Change String'] = (sp500_df['Close'].pct_change() * 100).round(2).astype(str) + ' %'
sp500_df_return = (sp500_df['Pct Change'] + 1).cumprod()[-1]

return_list = []
final_df = pd.DataFrame(columns=['Ticker', 'Latest Price', 'Score', 'PE_Ratio', 'PEG_Ratio', 'SMA_150', 'SMA_200', '52_Week_High', '52_Week_Low'])

for ticker in tickers:
    tk = yf.Ticker(ticker)
    df = tk.history(interval='1d', start=start, end=end)
    df.to_csv(f'stock_data/{ticker}.csv')
    df['Pct Change'] = df['Close'].pct_change()
    stock_return = (df['Pct Change'] + 1).cumprod()[-1]
    returns_compared = round((stock_return / sp500_df_return), 2)
    return_list.append(returns_compared)

best_performers = pd.DataFrame(list(zip(tickers, return_list)), columns=['Ticker', 'Returns Compared'])
best_performers['Score'] = best_performers['Returns Compared'].rank(pct=True) * 100
best_performers = best_performers[best_performers['Score'] >= best_performers['Score'].quantile(0.8)] # Top 20%


for ticker in best_performers['Ticker']:
    try:
        df = pd.read_csv(f'stock_data/{ticker}.csv', index_col=0)
        moving_averages = [150, 200]
        for ma in moving_averages:
            df[f'SMA_{ma}'] = round(df['Close'].rolling(window=ma).mean(), 2)

        latest_price = df['Close'][-1]
        moving_average_150 = df['SMA_150'][-1]
        moving_average_200 = df['SMA_200'][-1]
        low_52week = round(min(df['Low'][-52*5:]), 2)
        high_52week = round(max(df['High'][-52*5:]), 2)
        pe_ratio = round(yf.Ticker(ticker).info['trailingPE'], 2)
        peg_ratio = round(yf.Ticker(ticker).info['trailingPegRatio'], 2)
        score = round(best_performers[best_performers['Ticker'] == ticker]['Score'].to_list()[0], 2)

        conditions = [
            latest_price > moving_average_150 > moving_average_200,
            latest_price >= (1.3 * low_52week),
            latest_price >= (0.75 * high_52week),
            pe_ratio < 40,
            peg_ratio < 2
        ]

        if all(conditions):
            final_df = pd.concat([final_df, pd.DataFrame({
                'Ticker': [ticker],
                'Latest Price': [latest_price],
                'Score': [score],
                'PE_Ratio': [pe_ratio],
                'PEG_Ratio': [peg_ratio],
                'SMA_150': [moving_average_150],
                'SMA_200': [moving_average_200],
                '52_Week_High': [high_52week],
                '52_Week_Low': [low_52week]
            })], ignore_index=True)

    except Exception as e:
        print(f"Could not process {ticker}: {e}")
        continue 


final_df = final_df.sort_values(by='Score', ascending=False)
pd.set_option('display.max_columns', 10)
print(final_df)
final_df.to_csv('final_list.csv', index=False)