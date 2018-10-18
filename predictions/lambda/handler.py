import json
import requests
from collections import defaultdict
from fuzzywuzzy import process
from random import sample

# Constants


"""
Constants for default responses that do not need any further computation.
"""
DEFAULT_STOP_RESPONSE = 'All right. See you next time!'
DEFAULT_ERROR_MESSAGE = "I'm sorry. I don't know how to do that yet."
DEFAULT_HELP_MESSAGE = "Try asking me about prediction markets. Ask me to look up midterm elections."
PREDEFINED_RESPONSES = {
    'AMAZON.FallbackIntent': "I couldn't understand what you were asking. Why don't you ask me about elections?",
    'AMAZON.CancelIntent': DEFAULT_STOP_RESPONSE,
    'AMAZON.HelpIntent': DEFAULT_HELP_MESSAGE,
    'AMAZON.StopIntent': DEFAULT_STOP_RESPONSE,
    'AMAZON.NavigateHomeIntent': DEFAULT_STOP_RESPONSE,
}

"""
To be considered as a match, any other title would have to be within this percentage of the score of the best match.
"""
PERCENTAGE_THRESHOLD = 0.1

# API Helpers


def get_all_markets():
    """
    Query the PredictIt API to get all available markets in a dictionary that maps from the name of the market to its ID.
    """
    all_markets = requests.request(
        'GET', 'https://www.predictit.org/api/marketdata/all/')
    all_markets = json.loads(all_markets.content)
    return dict((market['name'], market['id']) for market in all_markets['markets'])


def get_market(id):
    """
    Query the PredictIt API to get the details of a particular market given the market's ID.
    """
    market = requests.request(
        'GET', "https://www.predictit.org/api/marketdata/markets/%d" % id)
    return json.loads(market.content)

# "UI" Helpers


def market_message(market):
    """
    Given the response from `get_market`, generates a message that conveys the relevant information of the particular market.
    """
    if len(market['contracts']) > 1:
        return "%s is too complicated." % market['name']
    return "%s is trading at %d percent." % \
        (market['name'], market['contracts'][0]['lastTradePrice'] * 100)


def response_from_message(message):
    """
    Helper to wrap a message string into the minimum acceptable Alexa response JSON.
    """
    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': message,
            }
        }
    }


def can_fulfill(intent):
    if intent['name'] == 'Query' and intent['slots'] and \
            intent['slots']['Market'] and intent['slots']['Market']['value']:
        return {
            'version': '1.0',
            'response': {
                'canFulfillIntent': {
                    'canFulfill': 'YES',
                    'slots': {
                        'Market': {
                            'canUnderstand': 'YES',
                            'canFulfill': 'YES'
                        },
                    }
                }
            }
        }
    return {
        'version': '1.0',
        'response': {
            'canFulfillIntent': {
                'canFulfill': 'NO',
            }
        }
    }

# Main function


def main(event, context):
    """
    Entry point for the Alexa action.
    """
    request_type = event['request']['type']
    if request_type != 'IntentRequest':
        if request_type == 'LaunchRequest':
            return response_from_message(DEFAULT_HELP_MESSAGE)
        elif request_type == 'CanFulfillIntentRequest':
            return can_fulfill(event['request']['intent'])
        elif request_type == 'SessionEndedRequest':
            return
    intent = event['request']['intent']
    intent_type = intent['name']
    # Get the canned responses out of the way before we do any heavy lifting
    # with external API calls.
    if intent_type in PREDEFINED_RESPONSES:
        return response_from_message(PREDEFINED_RESPONSES[intent_type])
    # Sanity check.
    if intent_type != 'Query' or 'Market' not in intent['slots']:
        return response_from_message(DEFAULT_ERROR_MESSAGE)
    keyword = intent['slots']['Market']['value']
    markets = get_all_markets()
    # Only take the ones that are within percentage threshold of the first
    # result. Bucket them by score.
    likely_markets = process.extract(keyword, markets.keys(), limit=100)
    (_, best_score) = likely_markets[0]
    result_markets = defaultdict(list)  # Multimap score -> id's
    for (name, score) in likely_markets:
        if best_score - score <= PERCENTAGE_THRESHOLD * best_score:
            result_markets[score].append(markets[name])
    # List of market JSON response's.
    result_markets = [get_market(id) for id in sum(
        [sample(ids, 1) for (_, ids) in result_markets.items()], [])]
    return response_from_message(' '.join(market_message(market) for market in result_markets))
