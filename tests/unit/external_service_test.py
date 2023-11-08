import src.bootstrap_resources.load_env_vars
from src.bootstrap_resources.flask_app import app

# initialise mongoDb before any  other imports that require DB
from src.bootstrap_resources.mongodb import initialize_mongodb
initialize_mongodb(app)

import unittest
from unittest.mock import patch, Mock

from src.services.external_service import get_paragraph, get_definition


class ExternalServiceTest(unittest.TestCase):

    @patch('src.services.external_service.requests')
    def test_search_paragraphs(self, requests_mock):
        # ARRANGE
        mock_response_text = 'Sample response'
        requests_mock.Session().get().status_code = 200
        requests_mock.Session().get().text = mock_response_text

        paragraphs_count_to_fetch = 1;
        sentences_in_paragraph = 30;

        # ACT
        response = get_paragraph(paragraphs_count_to_fetch, sentences_in_paragraph)

        # ASSERT
        # assert that the response returned by the network request is returned in the function response
        self.assertEqual(response, mock_response_text)

    @patch('src.services.external_service.requests')
    def test_get_paragraph_network_call_params(self, requests_mock):
        # ARRANGE
        paragraphs_count_to_fetch = 1;
        sentences_in_paragraph = 30;
        expected_url = f'http://metaphorpsum.com/paragraphs/{paragraphs_count_to_fetch}/{sentences_in_paragraph}'

        requests_mock.Session().get().status_code = 200
        requests_mock.Session().get().text = ''

        # ACT
        get_paragraph(paragraphs_count_to_fetch, sentences_in_paragraph)

        # ASSERT
        requests_mock.Session().get.assert_called_with(expected_url)

    @patch('src.services.external_service.requests')
    def test_get_definition_success(self, requests_mock):
        # ARRANGE
        requests_mock.Session().get().status_code = 200
        requests_mock.Session().get().text =  '''[
            {
                "word":"random",
                "phonetic":"/random/",
                "phonetics":[
                    {"text":"/random/","audio":""},
                    {
                        "text":"/random/",
                        "audio":"https://api.dictionaryapi.dev/media/pronunciations/en/random-uk.mp3",
                        "sourceUrl":"https://commons.wikimedia.org/w/index.php?curid=55508165",
                        "license":{"name":"BY-SA 4.0","url":"https://creativecommons.org/licenses/by-sa/4.0"}
                    },
                    {
                        "text":"/fʌk/","audio":"https://api.dictionaryapi.dev/media/pronunciations/en/random-us.mp3",
                        "sourceUrl":"https://commons.wikimedia.org/w/index.php?curid=930075",
                        "license":{"name":"BY-SA 3.0","url":"https://creativecommons.org/licenses/by-sa/3.0"}
                    }
                ],
                "meanings":[
                    {
                        "partOfSpeech":"noun",
                        "definitions":[
                            {"definition":"mock definition","synonyms":[],"antonyms":[]}
                        ]
                    }
                ]
            }
        ]'''


        # ACT
        response = get_definition('random')

        # ASSERT
        self.assertEqual(response, 'mock definition')


    @patch('src.services.external_service.requests')
    def test_get_definition_failure(self, requests_mock):
        # ARRANGE
        requests_mock.Session().get().status_code = 200
        requests_mock.Session().get().text =  '''{
            "title":"No Definitions Found",
            "message":"Sorry pal, we couldn't find definitions for the word you were looking for.",
            "resolution":"You can try the search again at later time or head to the web instead."
        }'''

        expected_result_when_definition_not_found = 'Definition not available';

        # ACT
        response = get_definition('random')

        # ASSERT
        self.assertEqual(response, expected_result_when_definition_not_found)

    @patch('src.services.external_service.requests')
    def test_get_definition_network_call_params(self, requests_mock):
        # ARRANGE
        find_definition_for_word = 'random'
        expected_url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{find_definition_for_word}'

        requests_mock.Session().get().status_code = 200
        requests_mock.Session().get().text = ''

        # ACT
        get_definition(find_definition_for_word)

        # ASSERT
        requests_mock.Session().get.assert_called_with(expected_url)