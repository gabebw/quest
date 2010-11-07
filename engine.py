"""The actual engine that interfaces with and sends SQL code to the DB."""

import sys

from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text
import sqlalchemy.exc

import config as config
from query import query_cache
import util

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
    If number_of_rows is None, then it checks config settings. For more
    information, see the documentation in the config module.
    """
    if query is None:
        raise ValueError("query cannot be None!")

    result = connection.execute(query)
    # Fetch the correct number of rows
    if number_of_rows is None:
        # Nothing specified, consult config.
        if config.ROWS_TO_SHOW == config.ALL_ROWS:
            return result.fetchall()
        else:
            if util.is_integer(config.ROWS_TO_SHOW):
                fetched_rows = result.fetchmany(config.ROWS_TO_SHOW)
                # Since number_of_rows_to_show may be less than the total number of
                # rows, and the ResultProxy only closes when all rows are exhausted,
                # explicitly close the ResultProxy.
                result.close()
                return fetched_rows
            else:
                raise ValueError("number_of_rows ({}) is not an int!".format(number_of_rows))
    else:
        if util.is_integer(number_of_rows):
            fetched_rows = result.fetchmany(int(number_of_rows))
            # Since number_of_rows may be less than the total number of
            # rows, and the ResultProxy only closes when all rows are exhausted,
            # explicitly close the ResultProxy.
            result.close()
            return fetched_rows
        else:
            raise ValueError("number_of_rows ({}) is not an int!".format(number_of_rows))
