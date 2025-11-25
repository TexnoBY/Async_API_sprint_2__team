from datetime import datetime
from typing import Generator

import psycopg
from elasticsearch_dsl import (
    Document,
    Keyword,
    MetaField,
    Text,
)
from psycopg import ServerCursor
from psycopg.conninfo import make_conninfo
from psycopg.rows import class_row


class Genre(Document):
    id = Keyword()
    name = Text(analyzer='ru_en')
    description = Text(analyzer='ru_en')
    last_change_date = Keyword(index=False)

    class Meta:
        dynamic = MetaField('strict')

    class Index:
        name = 'genres'
        settings = {
            'refresh_interval': '1s',
            'analysis': {
                'filter': {
                    'english_stop': {'type': 'stop', 'stopwords': '_english_'},
                    'english_stemmer': {'type': 'stemmer', 'language': 'english'},
                    'english_possessive_stemmer': {
                        'type': 'stemmer',
                        'language': 'possessive_english',
                    },
                    'russian_stop': {'type': 'stop', 'stopwords': '_russian_'},
                    'russian_stemmer': {'type': 'stemmer', 'language': 'russian'},
                },
                'analyzer': {
                    'ru_en': {
                        'tokenizer': 'standard',
                        'filter': [
                            'lowercase',
                            'english_stop',
                            'english_stemmer',
                            'english_possessive_stemmer',
                            'russian_stop',
                            'russian_stemmer',
                        ],
                    }
                },
            },
        }


def get_genres_index_data(
        database_settings: dict,
        last_sync_state: datetime,
        batch_size: int = 100
) -> Generator[list[Genre], None, None]:
    dsn = make_conninfo(**database_settings)

    with psycopg.connect(dsn, row_factory=class_row(Genre)) as conn, ServerCursor(conn, 'fetcher') as cursor:
        query = """
                    SELECT 
                        id, 
                        name, 
                        description, 
                        modified AS last_change_date
                    FROM content.genre
                    WHERE modified >= %s
                """
        cursor.execute(query, (last_sync_state,))

        while results := cursor.fetchmany(size=batch_size):
            yield results
