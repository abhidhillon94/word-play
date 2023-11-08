from flask import Blueprint, request
import re
from src.services.paragraph_service import search_paragraphs, store_paragraph, get_most_used_words_with_definitions
from src.services.external_service import get_paragraph

paragraphsBlueprint = Blueprint('paragraphs', __name__)


@paragraphsBlueprint.route('/search')
def search():
    # TODO: Add pagination capability

    search_terms = search_operator = ''
    # format the request params
    
    if request.args.get('search_terms'):
        search_terms = re.sub('[^a-zA-Z0-9 \n\.]', ' ', request.args.get('search_terms'))
    
    if request.args.get('search_operator'):
        search_operator = request.args.get('search_operator').lower()

    # validate the request
    if len(search_terms) == 0:
        return {'message': 'search_terms param is required in the query string'}, 400
    elif search_operator not in ['and', 'or']:
        return {'message': 'search_operator param containing either AND or OR value is required in the query string'}, 400

    # find the search results
    paragraphs = search_paragraphs(search_terms, search_operator)

    return {'paragraphs': paragraphs}


@paragraphsBlueprint.route('/', methods=['GET'])
def get_paragraphs():
    # fetch the paragraph from pargraph generator service
    paragraph_content = get_paragraph(1, 50)

    store_paragraph(paragraph_content)

    return {'paragraph': paragraph_content}


@paragraphsBlueprint.route('/dictionary', methods=['GET'])
def dictionary():
    words = get_most_used_words_with_definitions()
    return {'words': words}
