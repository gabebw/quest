#!/usr/bin/env python
"""
This can be run from the command line, to set up a test MySQL database.
The command-line usage is like:
    $ createDB.py csv_file_name db_name, table_name db_user db_password
Or, you can create a file containing the following:
    from quest.test import createDB
    createDB.create_db_from_csv_file(csv_file, db_name, table_name, db_username, db_password)
create_db_from_csv_file only allows one table to be created from the
given csv_file.  It assumes that the csv file is formatted like so:
    col_name1,col_name2,...,last_col_name
    type_of_col1,type_of_col2,...,type_of_last_column
    primary_key_boolean1,primary_key_boolean2,...,primary_key_boolean_for_last_column
    # Every line after this is a row where the i'th item is the row's
    # value for the i'th column

The second row, with the type_of_col1, allows for 3 types: STRING, INTEGER, or REAL (a non-integer).
The third row, with primary_key_boolean's, should have the string "TRUE" if this column is part of the primary key, and "FALSE" if it is not.
"""

import sys
import csv

# When we hit a warning, turn it into an error so we crash and get a
# stack trace.
import warnings
warnings.simplefilter('error')

try:
    import MySQLdb
except ImportError:
    sys.exit("ERROR: install mysql-python.")

try:
    import sqlalchemy
    from sqlalchemy import create_engine, MetaData, Table, Column
    from sqlalchemy import Integer, Numeric, Unicode
except ImportError:
    sys.exit("ERROR: install sqlalchemy.")

# global vars (initialized in initialize_db)
engine = None
metadata = None
connection = None

def create_db_from_csv_file(file_name, db_name, table_name, user, password):
    """
    Takes a filename to parse, db_name to write, and table_name to
    create and populate.
    """

    csv_file = csv.reader(open(file_name))
    column_names = [elem.strip() for elem in csv_file.next()]
    column_types = derive_column_types(csv_file.next())
    primary_keys = derive_keys(csv_file.next())

    # the rest of the CSV file
    data = list(csv_file)

    # initialize db, create table with metadata, populate table with data
    initialize_db(db_name, user, password)
    data = cleanup_data(data, column_types)
    table = create_table(table_name, column_names, column_types, primary_keys)
    populate_table(table, column_names, data)

def cleanup_data(rows, column_types):
    """
    Given an array of rows and an array of column_types (where the i-th
    item in column_types is the type of the i-th item in a given row), clean up
    and normalize the data so that e.g. all items in a Numeric column
    are numeric.
    """

    # Perform matrix transposition so that each item in rows becomes a
    # column
    columns = zip(*rows)
    def cleanup_numeric(elem, numeric_type):
        # Change '-' and '' to 0
        if str(elem).strip() in ['-', '']:
            return 0
        else:
            try:
                return numeric_type(elem.strip())
            except ValueError, ve:
                print "|%s|" % elem.strip()
                print ve
                raise TypeError("%s is of wrong type (expected %s, got %s)" % (element, numeric_type, type(element)))

    for index, column_type in enumerate(column_types):
        if isinstance(column_type, sqlalchemy.types.Integer):
            columns[index] = [cleanup_numeric(elem, int) for elem in columns[index]]
        elif isinstance(column_type, sqlalchemy.types.Numeric):
            columns[index] = [cleanup_numeric(elem, float) for elem in columns[index]]
        elif isinstance(column_type, sqlalchemy.types.Unicode):
            # Convert to unicode
            columns[index] = [unicode(elem) for elem in columns[index]]

    # Transpose again to get the rows back out
    rows = zip(*columns)
    return rows

def initialize_db(db_name, user, password):
    """
    Sets global connection, metadata, and engine variables. Also
    DROPs and then CREATEs the database.

    Multiple DBs can be created, so long as they have unique varNames.
    This will be useful when needing to read from one db and write to
    another(e.g. temp db in mem).
    """
    global engine, metadata, connection
    engine = create_engine('mysql://' + user + ':' + password + '@localhost:3306/' + db_name)
    engine.echo = False
    metadata = MetaData(engine)
    connection = engine.connect()
    # Create DB
    connection.execute("DROP DATABASE IF EXISTS baseball")
    connection.execute("CREATE DATABASE baseball")

def derive_keys(lst):
    # CSV file has "TRUE" in i'th column if i'th column should be a
    # primary key, and "FALSE" if it shouldn't
    booleanValues = []
    for element in lst:
        element = element.strip()
        if element == "TRUE":
            booleanValues.append(True)
        elif element == "FALSE":
            booleanValues.append(False)
        else:
            raise TypeError("Invalid type (should be TRUE or FALSE): %s" % element)
    return booleanValues

def derive_column_types(lst):
    """Map a string description of a type to a real sqlalchemy type."""
    column_types = []
    description2type = {
            # 15 is big enough for everything in the CSV file
            'String': sqlalchemy.Unicode(15),
            'Integer': sqlalchemy.Integer(),
            # precision = total number of digits in the number
            # scale = number of digits to right of decimal
            'Real': sqlalchemy.Numeric(precision=12, scale=6)
            }

    for element in lst:
        element = element.strip()
        if element in description2type:
            column_types.append(description2type[element])
        else:
            raise TypeError("Invalid type: %s" % element)
    return column_types

def create_table(table_name, column_names, column_types, keyValues):
    """
    Takes the metadata as parameters, using it to create the table.
    keyValues is an array of True/False values that indicate whether a
    given column is a primary key.
    """
    if not valid_list_lengths(column_names, column_types, keyValues):
        raise Exception("Invalid list lengths!")
    zipped = zip(column_names, column_types, keyValues)
    columns = [Column(col_name, col_type, primary_key=is_primary_key) for (col_name, col_type, is_primary_key) in zipped]
    table = Table(table_name, metadata, *columns)#, mysql_charset = 'utf8')
    table.create()
    return table

def valid_list_lengths(column_names, column_types, keyValues):
    """
    A helper function for create_table that takes the metadata as a
    parameter. Returns True if all lists are of same length, False
    otherwise.
    """
    if len(column_names) != len(column_types):
        print 'len(column_names) != len(column_types)'
        return False
    if len(column_types) != len(keyValues):
        print 'len(column_types) != len(keyValues)'
        return False
    return True

def populate_table(table, column_names, data):
    update = table.insert()
    [update.execute(dict(zip(column_names, element))) for element in data]

if __name__ == "__main__":
    if len(sys.argv) != 6:
        sys.exit("Usage: %s csv_file_name db_name table_name db_user db_password" % __file__)

    csv_file, db_name, table_name, db_user, db_password = [str(x) for x in sys.argv[1:]]
    print 'csv_file_name: ' + csv_file
    print 'db_name      : ' + db_name
    print 'table_name   : ' + table_name
    print 'db_user      : ' + db_user
    print 'db_password  : ' + db_password
    print

    print "Creating database..."
    create_db_from_csv_file(csv_file, db_name, table_name, db_user, db_password)
    print "done!"
