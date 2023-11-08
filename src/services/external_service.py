import requests
import json

from requests.adapters import HTTPAdapter, Retry


def get_paragraph(paragraphs_count, sentences_count):
    session = requests.Session()
    retries = Retry(total=3,
                    backoff_factor=0.1)
    session.mount('http://', HTTPAdapter(max_retries=retries))
    network_response = session.get('http://metaphorpsum.com/paragraphs/{paragraphs_count}/{sentences_count}'.format(
        paragraphs_count=paragraphs_count, sentences_count=sentences_count))

    return network_response.text


def get_definition(word):
    session = requests.Session()
    retries = Retry(total=3,
                    backoff_factor=0.1)
    session.mount('http://', HTTPAdapter(max_retries=retries))
    network_response = session.get('https://api.dictionaryapi.dev/api/v2/entries/en/{word}'.format(word=word))

    try:
        res = json.loads(network_response.text)
        return res[0]['meanings'][0]['definitions'][0]['definition']
    except:
        return 'Definition not available'
