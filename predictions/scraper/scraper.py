from requests import request
from json import loads
from itertools import combinations
from random import sample

# from IPython.core.debugger import Tracer; debug_here = Tracer()

# https://www.predictit.org/api/marketdata/markets/3633

all_markets = request('GET', 'https://www.predictit.org/api/marketdata/all/')
all_markets = loads(all_markets.content)

common_words = []
with open('common_words.txt', 'r') as f:
    common_words = set(f.read().splitlines())

with open('predictions.csv', 'w') as f:
    keywords = set() # Sample of some keyword utterances we want Alexa to learn.
    for market in all_markets['markets']:
        full_title = market['name'].replace(',','').replace('?','').replace('"','').lower()
        keywords.add(full_title)
        # Some subset of the words in the title that are relevant.
        relevant_words = [x for x in full_title.split() if not x in common_words]
        for i in range(1, len(relevant_words)):
            # 2 is the magic number because any more and we could overrun the sample size.
            keywords.update(sample(list(' '.join(list(x)) for x in combinations(relevant_words, i)), 2))
        # debug_here()
    for invocation in keywords:
        f.write(invocation + ",\n")