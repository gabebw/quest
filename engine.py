"""The actual engine that interfaces with and sends SQL code to the DB."""

import sys

import MySQLdb

import config
from query import query_cache
import util

db = MySQLdb.connect(host = config.db_host,
        user = config.db_user,
        passwd = config.db_password,
        db = config.db_name)
cursor = db.cursor()

def run_sql(sql):
    """
    Sends a pure SQL expression to the DB and returns the result.
    After running this, use engine.cursor.fetchone() or
    engine.cursor.fetchalL() to fetch results. Returns the cursor
    object.
    """
    try:
        cursor.execute(query)
        return cursor
    except Exception as e:
        print e
        # Re-raise the error
        raise e

def show(query, number_of_rows = None):
    """Actually sends the given query to the database and returns the resulting
    rows as a list. A wrapper around run_sql.
    If number_of_rows is None, then it checks config settings. For more
    information, see the documentation in the config module.
    """
    if query is None:
        raise ValueError("query cannot be None!")

    run_sql(query)
    # Fetch the correct number of rows
    if number_of_rows is None:
        # Nothing specified, consult config.
        if config.ROWS_TO_SHOW == config.ALL_ROWS:
            return cursor.fetchall()
        else:
            if util.is_integer(config.ROWS_TO_SHOW):
                fetched_rows = cursor.fetchmany(config.ROWS_TO_SHOW)
                return fetched_rows
            else:
                raise ValueError("number_of_rows ({}) is not an int!".format(number_of_rows))
    else:
        if util.is_integer(number_of_rows):
            fetched_rows = cursor.fetchmany(int(number_of_rows))
            return fetched_rows
        else:
            raise ValueError("number_of_rows ({}) is not an int!".format(number_of_rows))
