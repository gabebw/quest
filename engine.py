"""The actual engine that interfaces with and sends SQL code to the DB."""

from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text
import sqlalchemy.exc

import config as config
from query import query_cache

# in-memory SQLite engine
sql_engine = create_engine('sqlite:///:memory:', echo=True)
connection = sql_engine.connect()

def run_sql(sql):
    """Sends a pure SQL expression to the DB and returns the result. A small
    wrapper around show().
    """
    t = text(sql)
    try:
        rows = show(t)
    except sqlalchemy.exc.OperationalError as oe:
        print oe
    else:
        # Everything went fine, proceed.
        print t
        return rows

def show(query, number_of_rows = None):
    """Actually sends the given query to the database and returns the resulting
    rows as a list.
    If number_of_rows is None, then it displays all rows in result. By default,
    Quest does not SHOW until the user specifically commands it. The <TODO: FILL
    ME IN> setting in config.py may be used to change the default to one of
    three settings:
    * SHOW_ALL: default to SHOWing every row of every command,
    * SHOW_N: default to SHOWing N rows of every command
              (where N = config.number_of_rows_to_show), or
    * SHOWing only when the user asks for it (i.e. the built-in default)
    """
    if query is None:
        raise ValueError("query cannot be None!")

    result = connection.execute(query)
    # Fetch the correct number of rows
    if number_of_rows is None:
        # Nothing specified, consult config.
        if config.show_behavior == config.SHOW_ALL:
            return result.fetchall()
        elif config.show_behavior == config.SHOW_N:
            fetched_rows = result.fetchmany(config.number_of_rows_to_show)
            # Since number_of_rows_to_show may be less than the total number of
            # rows, and the ResultProxy only closes when all rows are exhausted,
            # explicitly close the ResultProxy.
            result.close()
            return fetched_rows
        else:
            # Default to showing every row
            return result.fetchall()
    else:
        if str(number_of_rows).isdigit():
            fetched_rows = result.fetchmany(int(number_of_rows))
            # Since number_of_rows may be less than the total number of
            # rows, and the ResultProxy only closes when all rows are exhausted,
            # explicitly close the ResultProxy.
            result.close()
            return fetched_rows
        else:
            raise ValueError("number_of_rows ({}) is not an int!".format(number_of_rows))
