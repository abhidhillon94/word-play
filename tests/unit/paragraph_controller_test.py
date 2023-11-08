import src.bootstrap_resources.load_env_vars

from src.bootstrap_resources.flask_app import app

# initialise mongoDb before any  other imports that require DB
from src.bootstrap_resources.mongodb import initialize_mongodb
initialize_mongodb(app)

from src.controllers.paragraph_controller import paragraphsBlueprint

from unittest.mock import patch
import unittest

app.register_blueprint(paragraphsBlueprint)

class ParagraphControllerTest(unittest.TestCase):

    @patch('src.controllers.paragraph_controller.search_paragraphs')
    def test_search_with_valid_params(self, search_paragraphs_mock):
        # ARRANGE
        return_value_of_search_paragraphs_mock = ['sample para']
        search_paragraphs_mock.return_value = return_value_of_search_paragraphs_mock

        # ACT
        self.app = app.test_client()
        response = self.app.get('/search?search_terms=first,second&search_operator=and',
                                headers={"Content-Type": "application/json"})

        # ASSERT
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json['paragraphs'],
                         return_value_of_search_paragraphs_mock)

    @patch('src.controllers.paragraph_controller.search_paragraphs')
    def test_search_with_missing_search_terms(self, search_paragraphs_mock):
        # ARRANGE
        search_paragraphs_mock.return_value = ['sample para']

        # ACT
        self.app = app.test_client()
        response = self.app.get(
            '/search?search_operator=and', headers={"Content-Type": "application/json"})

        # ASSERT
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            response.json['message'], 'search_terms param is required in the query string')

    @patch('src.controllers.paragraph_controller.search_paragraphs')
    def test_search_with_missing_search_operator(self, search_paragraphs_mock):
        # ARRANGE
        search_paragraphs_mock.return_value = ['sample para']

        # ACT
        self.app = app.test_client()
        response = self.app.get(
            '/search?search_terms=qwe', headers={"Content-Type": "application/json"})

        # ASSERT
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            response.json['message'], 'search_operator param containing either AND or OR value is required in the query string')

    @patch('src.controllers.paragraph_controller.search_paragraphs')
    def test_search_with_invalid_search_operator(self, search_paragraphs_mock):
        # ARRANGE
        search_paragraphs_mock.return_value = ['sample para']

        # ACT
        self.app = app.test_client()
        response = self.app.get('/search?search_terms=qwe&search_operator=123',
                                headers={"Content-Type": "application/json"})

        # ASSERT
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            response.json['message'], 'search_operator param containing either AND or OR value is required in the query string')

    @patch('src.controllers.paragraph_controller.store_paragraph')
    @patch('src.controllers.paragraph_controller.get_paragraph')
    def test_get_paragraphs_return_value(self, get_paragraph_mock, store_paragraph_mock):
        # ARRANGE
        return_value_of_get_paragraph_mock = 'random para'
        get_paragraph_mock.return_value = return_value_of_get_paragraph_mock

        # ACT
        self.app = app.test_client()
        response = self.app.get(
            '/', headers={"Content-Type": "application/json"})

        # ASSERT
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json['paragraph'],
                         return_value_of_get_paragraph_mock)

    @patch('src.controllers.paragraph_controller.get_most_used_words_with_definitions')
    def test_dictionary_return_value(self, get_most_used_words_with_definitions_mock):
        # ARRANGE
        most_used_words_sample = {
            "words": [
                {
                    "definition": "(short scale) A million million: 1 followed by twelve zeros, 1012.",
                    "word": "trillion"
                },
                {
                    "definition": "Something that is posited; a postulate.",
                    "word": "posit"
                }
            ]
        }
        get_most_used_words_with_definitions_mock.return_value = most_used_words_sample

        # ACT
        self.app = app.test_client()
        response = self.app.get(
            '/dictionary', headers={"Content-Type": "application/json"})

        # ASSERT
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json['words'], most_used_words_sample)
