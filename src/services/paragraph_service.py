from src.bootstrap_resources.elasticsearch_client import elasticsearch_client
from src.models.Paragraph import Paragraph
from src.models.WordsCount import WordsCount
from src.jobs.precompute_words_count import precompute_word_counts_and_definitions

def search_paragraphs(search_terms, search_operator):
    body = {
        "query": {
            "match": {
                "para_content": {
                    "query": search_terms,
                    "operator": search_operator
                }
            }
        }
    }
    res = elasticsearch_client.search(index="paragraphs", body=body)

    paragraphs = []
    for matchingDocs in res['hits']['hits']:
        paragraphs.append({
            'id': matchingDocs['_id'], 'para_content': matchingDocs['_source']['para_content']})

    return paragraphs


def store_paragraph(paragraph_content):
    # persit the para in mongo
    res = Paragraph(para_content=paragraph_content).save()

    # index the para in elasticsearch
    elasticsearch_client.index(index='paragraphs', id=res.id, body={
        'para_content': paragraph_content})

    precompute_word_counts_and_definitions.delay(paragraph_content)

def get_most_used_words_with_definitions():
    word_counts = WordsCount.objects().order_by('-global_occurance_count').order_by('_id').limit(10)
    res = [{'word': word_count.word, 'definition': word_count.definition} for word_count in word_counts]
    return res
