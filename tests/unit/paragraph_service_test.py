import src.bootstrap_resources.load_env_vars
from src.bootstrap_resources.flask_app import app

# initialise mongoDb before any  other imports that require DB
from src.bootstrap_resources.mongodb import initialize_mongodb
initialize_mongodb(app)

import unittest
from unittest.mock import patch, Mock

from src.services.paragraph_service import search_paragraphs, get_most_used_words_with_definitions, store_paragraph
from src.models.WordsCount import WordsCount
from src.models.Paragraph import Paragraph


elasticsearch_query_result = {
    'took': 125,
    'timed_out': False,
    '_shards': {'total': 1, 'successful': 1, 'skipped': 0, 'failed': 0},
    'hits': {'total': {'value': 3, 'relation': 'eq'}, 'max_score': 1.5848469,
             'hits': [
        {'_index': 'paragraphs', '_id': '654b4095c5982e15207f9894',
         '_score': 1.5848469, '_source': {'para_content': "result one"}},
        {'_index': 'paragraphs', '_id': '65497e64eda3051fba3c3aa2',
         '_score': 1.3273889, '_source': {'para_content': "result two"}},
        {'_index': 'paragraphs', '_id': '654a8d97d81061cdabf703b6',
         '_score': 1.261767, '_source': {'para_content': "result three"}}
    ]}}


class ParagraphServiceTest(unittest.TestCase):

    @patch('src.services.paragraph_service.elasticsearch_client')
    def test_search_paragraphs_to_return_parsed_elastic_response(self, elasticsearch_client_mock):
        # ARRANGE
        elasticsearch_client_mock.search.return_value = elasticsearch_query_result

        # ACT
        response = search_paragraphs('mockparam1', 'mockparam2')

        # ASSERT
        self.assertEqual(response, [{'id': '654b4095c5982e15207f9894', 'para_content': "result one"},
                                    {'id': '65497e64eda3051fba3c3aa2',
                                        'para_content': "result two"},
                                    {'id': '654a8d97d81061cdabf703b6', 'para_content': "result three"}])

    @patch('src.services.paragraph_service.elasticsearch_client')
    def test_search_paragraphs_to_generate_elastic_query(self, elasticsearch_client_mock):
        # ARRANGE
        elasticsearch_client_mock.search.return_value = elasticsearch_query_result

        expected_elasticsearch_query = {
            "query": {
                "match": {
                    "para_content": {
                        "query": 'searchterm1 searchterm2',
                        "operator": 'and'
                    }
                }
            }
        }

        # ACT
        search_paragraphs('searchterm1 searchterm2', 'and')

        # ASSERT
        # self.assertEqual(elasticsearch_client_mock.search.call_args[1], body=expected_elasticsearch_query)
        elasticsearch_client_mock.search.assert_called_with(
            index='paragraphs', body=expected_elasticsearch_query)


    @patch('src.services.paragraph_service.precompute_word_counts_and_definitions')
    @patch('src.services.paragraph_service.Paragraph')
    @patch('src.services.paragraph_service.elasticsearch_client')
    def test_store_paragraph_to_persit_content_in_mongo_and_elastic(self, elasticsearch_client_mock, paragraph_mock, precompute_word_counts_and_definitions_mock):
        # ARRANGE
        paragraph_content_arg = 'mock content'

        # paragraph_mock.save.return_value = Paragraph(
        #     id='sample_id',para_content=paragraph_content_arg)

        # TODO: avoid chaining and get the above commented code to work
        paragraph_return_value_mock = Mock()
        paragraph_return_value_mock.save.return_value = Paragraph(
            id='sample_id',para_content=paragraph_content_arg)
        paragraph_mock.return_value = paragraph_return_value_mock

        # ACT
        store_paragraph(paragraph_content_arg)

        # ASSERT
        paragraph_mock.assert_called_with(para_content=paragraph_content_arg)
        elasticsearch_client_mock.index.assert_called_with(
            index='paragraphs', id='sample_id', body={'para_content': paragraph_content_arg})

    @patch('src.services.paragraph_service.WordsCount')
    def test_get_most_used_words_with_definitions(self, words_count_mock):
        # ARRANGE
        words_count_mock.objects().order_by().order_by().limit.return_value = [
            WordsCount(word='word1', definition='definition1'),
            WordsCount(word='word2', definition='definition2'),
            WordsCount(word='word3', definition='definition3'),
        ]

        # ACT
        response = get_most_used_words_with_definitions()

        # ASSERT
        self.assertEqual(response, [
            {'word': 'word1', 'definition': 'definition1'},
            {'word': 'word2', 'definition': 'definition2'},
            {'word': 'word3', 'definition': 'definition3'}
        ])
