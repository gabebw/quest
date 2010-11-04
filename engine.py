"""The actual engine that interfaces with and sends SQL code to the DB."""

from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text
import sqlalchemy.exc

import quest.operators
import quest.config
from quest.query import query_cache

# in-memory SQLite engine
sql_engine = create_engine('sqlite:///:memory:', echo=True)
connection = sql_engine.connect()

def run_sql(sql):
    """Evaluates a pure SQL expression."""
    t = text(sql)
    try:
        response = connection.execute(t)
    except sqlalchemy.exc.OperationalError as oe:
        print oe
    else:
        # Everything went fine, proceed.
        print t


def show(query, number_of_rows = None):
    """Actually sends the given query to the database and returns the result.
    If query is None, then it uses the most recent query. If number_of_rows is
    None, then it displays all rows in result. By default, Quest does not SHOW
    until the user specifically commands it. The <FILL ME IN> setting may be
    used to change the default to one of three settings:
    * default to SHOWing every row of every command,
    * default to SHOWing N rows of every command (where N is an integer), or
    * default to SHOWing only when the user asks for it (i.e. the default
      anyway)
    """
    if query is None:
        query = query_cache.most_recent_query()
    if number_of_rows is None:
        number_of_rows = quest.config.number_of_rows_to_show

    return connection.execute(query)
