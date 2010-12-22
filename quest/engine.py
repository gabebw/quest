"""The actual engine that interfaces with and sends SQL code to the DB."""

import sys

import MySQLdb

import config
import util

class QuestConnectionError(MySQLdb.MySQLError):
    def __init__(self, db_host, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

    def __str__(self):
        msg = "Couldn't connect! Maybe your connection info is wrong:"
        msg += "\ndb_host: %s" % self.db_host
        msg += "\ndb_user: %s" % self.db_user
        msg += "\ndb_password: %s" % self.db_password
        msg += "\ndb_name: %s" % self.db_name
        return msg

    def __repr__(self):
        return __str__()

# run_sql sets these the first time it's run. This enables us to import
# this file before setting config parameters
db = None
cursor = None

def run_sql(sql):
    """
    Sends a pure SQL expression to the DB and returns the DB cursor object.
    May raise an error, which it intentionally does not handle.

    After running this, use the returned cursor object to run
    cursor.fetchone() or cursor.fetchall() to fetch results.
    """
    global db, cursor

    if db is None:
        # Not yet set, do so

        try:
            db = MySQLdb.connect(host = config.db_host,
                    user = config.db_user,
                    passwd = config.db_password,
                    db = config.db_name)
        except MySQLdb.MySQLError, e:
            raise QuestConnectionError(config.db_host,
                    config.db_user,
                    config.db_password,
                    config.db_name)
        cursor = db.cursor()
    try:
        if not sql.endswith(';'):
            # We need a semicolon or pure SQL won't work
            sql += ';'
        cursor.execute(sql)
        return cursor
    except Exception, e:
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
                raise ValueError("number_of_rows (%d) is not an int!" % number_of_rows)
    else:
        if util.is_integer(number_of_rows):
            fetched_rows = cursor.fetchmany(int(number_of_rows))
            return fetched_rows
        else:
            raise ValueError("number_of_rows (%d) is not an int!" % number_of_rows)
