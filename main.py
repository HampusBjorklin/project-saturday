import requests
import matplotlib.pyplot as plt
from datetime import datetime
import datetime as dt
import json

'''
with open('Project-Saturday/OHLCV/OMXSPI/OMXSPI 2023-01-05.json') as f:
    data = json.load(f)

opening_prices = [data[row]['o'] for row in data]
closing_prices = [data[row]['c'] for row in data]
times = [datetime.strptime(time, '%H:%M:%S') for time in list(data.keys())]

plt.plot(times, closing_prices)

print(((closing_prices[-1]/opening_prices[0])-1)*100)
plt.grid()
plt.xticks(rotation=70)
plt.show()
'''