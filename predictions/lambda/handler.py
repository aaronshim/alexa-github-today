import json
import requests

def markets():
    all_markets = requests.request('GET', 'https://www.predictit.org/api/marketdata/all/')
    all_markets = json.loads(all_markets.content)
    return dict((market['name'], market['id']) for market in all_markets['markets'])

# Entry point
def alexa(event, context):
    print(event)
    print(markets())
    number = 10
    response = {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': 'Your lucky number is ' + str(number),
            }
        }
    }
    print(response)
    return response