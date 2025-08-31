from datetime import datetime
from typing import Generator

import psycopg
from elasticsearch_dsl import (
    Document,
    Float,
    InnerDoc,
    Keyword,
    MetaField,
    Nested,
    Text,
)
from psycopg import ServerCursor
from psycopg.conninfo import make_conninfo
from psycopg.rows import class_row

class FilmRole(InnerDoc):
    uuid = Keyword()
    roles = Keyword(multi=True)

    class Meta:
        dynamic = MetaField('strict')

class Person(Document):
    id = Keyword()
    full_name = Text(analyzer='ru_en')
    films = Nested(FilmRole)
    last_change_date = Keyword(index=False)

    class Index:
        name = 'person'
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

    class Meta:
        dynamic = MetaField('strict')


def get_person_index_data(
    database_settings: dict, last_sync_state: datetime, batch_size: int = 100
) -> Generator[list[Person], None, None]:

    dsn = make_conninfo(**database_settings)

    with psycopg.connect(dsn, row_factory=class_row(Person)) as conn, ServerCursor(conn, 'fetcher') as cursor:
        query = """
            SELECT 
                p.id, 
                p.full_name, 
                p.modified AS last_change_date,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'uuid', pf.film_work_id,
                            'roles', pf.role
                        )
                    ) FILTER (WHERE pf.film_work_id IS NOT NULL),
                    '[]'::json
                ) as films
            FROM content.person p
            LEFT JOIN content.person_film_work pf ON pf.person_id = p.id
            WHERE p.modified >= %s
            GROUP BY p.id, p.full_name, p.modified
        """


        cursor.execute(query, (last_sync_state,))
        while results := cursor.fetchmany(size=batch_size):
            yield results