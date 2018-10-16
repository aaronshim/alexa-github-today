import requests
import json

# from IPython.core.debugger import Tracer; debug_here = Tracer()

all_markets = requests.request('GET', 'https://www.predictit.org/api/marketdata/all/')
all_markets = json.loads(all_markets.content)
with open('predictions.csv', 'w') as f:
    for market in all_markets['markets']:
        f.write(market['name'].replace(",","") + "\n")


# https://www.predictit.org/api/marketdata/markets/3633