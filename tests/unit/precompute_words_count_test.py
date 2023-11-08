import src.bootstrap_resources.load_env_vars
from src.bootstrap_resources.flask_app import app

# initialise mongoDb before any  other imports that require DB
from src.bootstrap_resources.mongodb import initialize_mongodb
initialize_mongodb(app)

import unittest
from unittest.mock import patch, Mock, call

from src.jobs.precompute_words_count import precompute_word_counts_and_definitions
from src.models.WordsCount import WordsCount
from tests.helpers import are_lists_of_dicts_equal


class PrecomputeWordsCountTest(unittest.TestCase):

    @patch('src.jobs.precompute_words_count.WordsCount')
    @patch('src.jobs.precompute_words_count.elasticsearch_client')
    def test_precompute_word_counts_and_definitions_to_update_counter_of_existing_words(self, elasticsearch_client_mock, words_count_mock):
        # ARRANGE
        mock_paragraph_content = 'word1 word2 word3 word4 word5'

        words_existent_in_db = ['word1', 'word2', 'word5']
        mock_word_models_existent_in_db = [
            WordsCount(word='word1', global_occurance_count='10',
                       definition='word1 definition'),
            WordsCount(word='word2', global_occurance_count='10',
                       definition='word2 definition'),
            WordsCount(word='word5', global_occurance_count='10',
                       definition='word5 definition'),
        ]

        # mock the elasticsearch query call to fetch the analysed content (tokenized words)
        elasticsearch_client_mock.indices.analyze().body = {'tokens': [{'token': 'word1'}, {
            'token': 'word2'}, {'token': 'word3'}, {'token': 'word4'}, {'token': 'word5'}]}

        # mock the query that fetches existing words count from the DB
        words_count_mock.objects().only().as_pymongo.return_value = mock_word_models_existent_in_db

        # mock the query that fetches the top occuring words
        words_count_mock.objects().order_by().order_by().limit.return_value = []

        # ACT
        precompute_word_counts_and_definitions(mock_paragraph_content)

        # ASSERT
        # assert if word that are found in the DB are updated
        words_count_mock._get_collection().update_many.assert_called_with({'word': {'$in': words_existent_in_db}}, {
                                 '$inc': {'global_occurance_count': 1}}, True)


    @patch('src.jobs.precompute_words_count.WordsCount')
    @patch('src.jobs.precompute_words_count.elasticsearch_client')
    def test_precompute_word_counts_and_definitions_to_insert_new_words_in_db(self, elasticsearch_client_mock, words_count_mock):
        # ARRANGE
        mock_paragraph_content = 'word1 word2 word3 word4 word5'

        mock_word_models_existent_in_db = [
            WordsCount(word='word1', global_occurance_count='10',
                       definition='word1 definition'),
            WordsCount(word='word2', global_occurance_count='10',
                       definition='word2 definition'),
            WordsCount(word='word5', global_occurance_count='10',
                       definition='word5 definition'),
        ]

        words_non_existent_in_db = ['word3', 'word4']
        # prepare the documents that are expected to be inserted in the DB since they don't exist already
        expected_word_count_docs_to_be_inserted = [{'word': word, 'global_occurance_count': 1} for word in words_non_existent_in_db]

        # mock the elasticsearch query call to fetch the analysed content (tokenized words)
        elasticsearch_client_mock.indices.analyze().body = {'tokens': [{'token': 'word1'}, {
            'token': 'word2'}, {'token': 'word3'}, {'token': 'word4'}, {'token': 'word5'}]}

        # mock the query that fetches existing words count from the DB
        words_count_mock.objects().only().as_pymongo.return_value = mock_word_models_existent_in_db

        # mock the query that fetches the top occuring words
        words_count_mock.objects().order_by().order_by().limit.return_value = []

        # ACT
        precompute_word_counts_and_definitions(mock_paragraph_content)

        # ASSERT
        # assert if word that are not found in the DB are inserted
        is_word_count_docs_to_be_inserted_as_expected = are_lists_of_dicts_equal(
            words_count_mock._get_collection().insert_many.call_args.args[0],
            expected_word_count_docs_to_be_inserted
        )
        self.assertTrue(is_word_count_docs_to_be_inserted_as_expected, 'Word count docs to be inserted in the DB are not as expected')


    @patch('src.jobs.precompute_words_count.get_definition')
    @patch('src.jobs.precompute_words_count.WordsCount')
    @patch('src.jobs.precompute_words_count.elasticsearch_client')
    def test_precompute_word_counts_and_definitions_to_fetch_definitions_of_words_without_definition(self, elasticsearch_client_mock, words_count_mock, get_definition_mock):
        # ARRANGE
        mock_paragraph_content = 'word1 word2 word3 word4 word5'

        mock_word_models_existent_in_db = [
            WordsCount(word='word1', global_occurance_count='10', definition='word1 definition'),
            WordsCount(word='word2', global_occurance_count='10', definition='word2 definition'),
            WordsCount(word='word5', global_occurance_count='10', definition='word5 definition'),
        ]

        # mock the elasticsearch query call to fetch the analysed content (tokenized words)
        elasticsearch_client_mock.indices.analyze().body = {'tokens': [{'token': 'word1'}, {
            'token': 'word2'}, {'token': 'word3'}, {'token': 'word4'}, {'token': 'word5'}]}

        # mock the query that fetches existing words count from the DB
        words_count_mock.objects().only().as_pymongo.return_value = mock_word_models_existent_in_db

        # mock the query that fetches the top occuring words
        # return mocks instead of wordcount models since update() method gets called on the returned models and these are not saved yet
        words_count_mock.objects().order_by().order_by().limit.return_value = [
            Mock(word='word1', definition=None),
            Mock(word='word3', definition='definition 3'),
            Mock(word='word4', definition=None),
            Mock(word='word5', definition='definition 5')
        ];

        # ACT
        precompute_word_counts_and_definitions(mock_paragraph_content)

        # ASSERT
        # assert that words definitions have been fetched for the top used words found in the DB which did not have precomputed word definitions
        get_definition_mock.assert_has_calls([call('word1'), call('word4')], any_order=True)
        self.assertTrue(get_definition_mock.call_count == 2, 'get_definition function has been called more than twice but the expectation is only 2 times')
