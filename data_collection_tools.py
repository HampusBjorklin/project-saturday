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


def ccollect_history_nasdaq(isin, start_date='2015-01-01', end_date=str(datetime.today().date)):
    '''
    url = 'https://www.nasdaqomxnordic.com/webproxy/DataFeedProxy.aspx'
    xml = f"""<post>
            <param name="Exchange" value="NMF"/>
            <param name="SubSystem" value="History"/>
            <param name="Action" value="GetDataSeries"/>
            <param name="AppendIntraDay" value="no"/>
            <param name="Instrument" value="{isin}"/>
            <param name="FromDate" value="2023-01-01"/>
            <param name="ToDate" value="2023-03-01"/>
            <param name="hi__a" value="0,1,2,4,21,8,10,11,12"/>
            <param name="ext_xslt" value="/nordicV3/hi_table.xsl"/>
            <param name="ext_xslt_lang" value="sv"/>
            <param name="ext_xslt_hiddenattrs" value=",ip,iv,"/>
            <param name="ext_xslt_tableId" value="historicalTable"/>
            <param name="app" value="/index/historiska_kurser"/>
            </post>
        """
    response = requests.post(url, data=xml).text
    '''
    url = 'https://httpbin.org/headers'
    s = requests.session()
    text = s.get(url).text
    print(text)


ccollect_history_nasdaq('test')