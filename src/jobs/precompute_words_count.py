from src.bootstrap_resources.celery import celery
from src.bootstrap_resources.elasticsearch_client import elasticsearch_client
from src.models.WordsCount import WordsCount
from src.services.external_service import get_definition

# updates the count of words from the paragraph in the DB (new ones to be created and existing ones to be updated)
@celery.task(name="precompute_word_counts_and_definitions")
def precompute_word_counts_and_definitions(paragraph_content):

    # tokenize the content to get the reduced root words that elasticsearch stores
    analyzed_result = elasticsearch_client.indices.analyze(
        body={"analyzer": "english", "text": paragraph_content})

    tokenized_words = []
    for element in analyzed_result.body['tokens']:
        tokenized_words.append(element['token'])

    # find the words that already exist in the DB
    existing_words_result = WordsCount.objects(
        __raw__={'word': {'$in': tokenized_words}}).only('word').as_pymongo()

    existing_words = []
    for existing_word in existing_words_result:
        existing_words.append(existing_word['word'])

    # compute the words that don't exist in the DB
    non_existent_words = list(
        set(tokenized_words).symmetric_difference(existing_words))
    
    collection = WordsCount._get_collection()

    # bulk insert the words that do not exist in the DB
    collection.insert_many([{'word': word, 'global_occurance_count':1} for word in non_existent_words])

    # increment the word count of words that already exist
    collection.update_many({'word': {'$in': existing_words}}, {'$inc': {'global_occurance_count': 1}}, True)
    
    '''
    find the most used words and update the definitions if they don't exist
    we precompute definitions for top 30 words instead of 10 
    because their ranking could change before the definitions are fetched in this job
    and since we do not fetch the definitions realtime in the dictionary API call,
    we precompute for extra words (20 additional words) that are likely to make it to top 10
    '''
    word_counts = WordsCount.objects().order_by('-global_occurance_count').order_by('_id').limit(30)
    for word in word_counts:
        if not word.definition:
            definition = get_definition(word.word)
            word.update(definition=definition)

    return True