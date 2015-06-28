from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

schema = Schema(
    name = TEXT(stored=True),
    description = TEXT(stored=True)
)
index = create_in('index', schema)
writer = index.writer()

def load_database():
    videos = Videos.select().execute()
    for video in videos:
        writer.add_document(
            name = video.name,
            description = video.description
        )
    writer.commit()

def search_database(keyword):
    with index.searcher() as searcher:
        query = QueryParser('name', index.schema).parse(keyword)
        return searcher.search(query)
