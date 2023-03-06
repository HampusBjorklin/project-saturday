import requests
import json
from datetime import datetime
from datetime import timedelta
import sys
import re
import sqlite3


# Define tickers and their respectice avanza-api id to scrape from
tickers = {
    'Ethereum XBT': {'id': 791709, 'Country': 'SE'},
    'Bitcoin XBT': {'id': 563966, 'Country': 'SE'},
    'OMXS30': {'id': 19002, 'Country': 'SE'},
    'OMXSPI': {'id': 18988, 'Country': 'SE'},
    'DJ USA': {'id': 155458, 'Country': 'US'},
    'NASDAQ 100': {'id': 155541, 'Country': 'US'},
    'DAX': {'id': 18981, 'Country': 'DE'}
}
# Get ohlc

def collect_information():
    text = requests.get('https://www.avanza.se/frontend/template.html/marketing/advanced-filter/advanced-filter-template?1673133265395&widgets.marketCapitalInSek.filter.lower=&widgets.marketCapitalInSek.filter.upper=&widgets.marketCapitalInSek.active=true&widgets.stockLists.filter.list%5B0%5D=SE.LargeCap.SE&widgets.stockLists.filter.list%5B1%5D=SE.MidCap.SE&widgets.stockLists.active=true&widgets.numberOfOwners.filter.lower=&widgets.numberOfOwners.filter.upper=&widgets.numberOfOwners.active=true&parameters.startIndex=0&parameters.maxResults=500&parameters.selectedFields%5B0%5D=LATEST&parameters.selectedFields%5B1%5D=DEVELOPMENT_TODAY&parameters.selectedFields%5B2%5D=DEVELOPMENT_ONE_YEAR&parameters.selectedFields%5B3%5D=MARKET_CAPITAL_IN_SEK&parameters.selectedFields%5B4%5D=PRICE_PER_EARNINGS&parameters.selectedFields%5B5%5D=DIRECT_YIELD&parameters.selectedFields%5B6%5D=NBR_OF_OWNERS&parameters.selectedFields%5B7%5D=LIST')
    matches=re.findall(r'tools-trigger="[0-9]*"', text.text)
    orderbook_ids = [int(re.findall('\d+', match)[0]) for match in matches]
    for i in orderbook_ids:
        name = requests.get(f'https://www.avanza.se/_api/market-guide/stock/{i}').json()
        name = name['listing']['tickerSymbol']

def collect_ohlcv(ticker_dict):
    for ticker in ticker_dict:
        ticker_id = tickers[ticker]['id']
        print(ticker)
        ticker_country = tickers[ticker]['Country']

        if ticker_country == 'SE' or ticker_country == 'DE':
            time_delta = 1
        elif ticker_country == 'US':
            time_delta = -6

        data = requests.get(f'https://www.avanza.se/_api/price-chart/stock/{ticker_id}/?timePeriod=today&resolution=ten_minutes').json()
        todays_date = data['ohlc'][0]['timestamp']
        todays_date = datetime.utcfromtimestamp(todays_date/1000) + timedelta(hours=time_delta)
        todays_date = str(todays_date.date())
        ticks = {}
        for row in data['ohlc']:
            time = row['timestamp']
            dt = str((datetime.utcfromtimestamp(time/1000) + timedelta(hours=1)).time())
            ticks[dt] = {'o': round(row['open'], 3), 'h': round(row['high'], 3), 'l': round(row['low'], 3), 'c':round(row['close'], 3), 'v':row['totalVolumeTraded']}
    
        
        file_name = f'project-saturday/OHLCV/{ticker}/{ticker} {todays_date}.json'

        with open(file_name, 'w') as f:
                json.dump(ticks, f)


def collect_closing_prices_nasdaq(isin, db_cursor, start_date: datetime.date = datetime(2002, 1, 1).date(), end_date: datetime.date = datetime.today().date()):
    if end_date <= start_date:
        print('Invalid choice of input dates...')
        sys.exít(1)
    sql = f"SELECT DATE FROM {isin.upper()}"
    collected_dates = list(db_cursor.execute(sql))
    start = str(start_date)
    if len(collected_dates)>=1:
        last_collected_date = collected_dates[-1][0]
        next_date = datetime.strptime(last_collected_date, '%Y-%m-%d')+timedelta(days=1)
        start = str(next_date.date())

    end = str(end_date)
    print(start)
    print(end)
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    try:
        url = f'https://www.nasdaqomxnordic.com/webproxy/DataFeedProxy.aspx?SubSystem=History&Action=GetChartData&inst.an=id%2Cnm%2Cfnm%2Cisin%2Ctp%2Cchp%2Cycp&FromDate={start}&ToDate={end}&json=true&timezone=CET&showAdjusted=false&app=%2Findex%2Fhistoriska_kurser-HistoryChart&DefaultDecimals=false&Instrument={isin}'
        s = requests.session()
        json = s.get(url, headers=headers).json()
        data = json['data'][0]['chartData']['cp']
    except:
        print(f'Could not find data for ISIN {isin} between dates {start} -> {end}')
        sys.exit(1)

    for d in data:
        day = datetime.fromtimestamp(d[0]/1000).date()
        close = d[1]
        sql = f"""INSERT OR REPLACE INTO {isin.upper()} 
                  (DATE, CLOSING_PRICE) 
                  VALUES("{day}", {close});"""
        db_cursor.execute(sql)


db_conn = sqlite3.connect('Quotes.db')
db_cursor = db_conn.cursor()
collect_closing_prices_nasdaq('SE0000744195', db_cursor)
db_conn.commit()
db_conn.close()
