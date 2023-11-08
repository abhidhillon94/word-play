from elasticsearch import Elasticsearch
import os

elasticsearch_client = Elasticsearch(
            hosts=os.environ['ELASTICSEARCH_HOSTS'].split(','), timeout=3, max_retries=3, retry_on_timeout=True)
if elasticsearch_client.ping():
    print("Connected to elasticsearch")
else:
    print("Couldn't connect to elasticsearch")

index_mappings = {
    "properties": {
        "para_content": {
            "type": "text",
            "analyzer": "english"
        }
    }
}
try:
    elasticsearch_client.indices.create(index='paragraphs', mappings=index_mappings)
except:
    print("Elasticsearch index couldn't be created. Looks like it already exists")
