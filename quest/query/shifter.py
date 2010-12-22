import re
import datetime
from operator import itemgetter

import quest.engine

try:
    import MySQLdb
except ImportError:
    import sys
    sys.exit("!!! Could not import MySQLdb. Install mysql-python.")

# Raised when we couldn't shift on the supplied attribute
class DidNotShiftException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

# Magic constants.
RSHIFT = 0
LSHIFT = 1

# All of the ops that we match
all_ops = ('<>', '!=', '<=', '>=', '<', '>', '==', '=')
# Matches a date like YYYY-MM-DD
date_regexp = re.compile(r"\d{4}-\d{2}-\d{2}")
# Matches a time like HH:MM:SS
time_regexp = re.compile(r"\d{2}:\d{2}:\d{2}")

# Regexp to match a SQL equality operator
rOperator = re.compile(r'(%s)' % '|'.join(all_ops))
# Used to split a SQL string into meaningful chunks
rChunker = re.compile(r'(%s|\.|\s)' % '|'.join(all_ops))
rWhitespace = re.compile(r"\s+")
# Table name and quotes are both optional, so
# this matches any of:
#   att
#   "att"
#   tablename."att"
#   "tablename".att
#   "tablename"."att"
# match.groups(1) would be "att" (no quotes)
rBareAttribute = re.compile(r"(?:\w+\.)?[\"']?(\w+)[\"']?")

# Maps a column name to its type, e.g. movie_id => int
meta_dict = {}

# DB cursor
cursor = None
# A list of all of the column names
column_names = None

# Result from executing query in connect(query)
result_rows = None

def findOperator(string):
    """
    If _string_ contains an operator from all_ops, returns that operator.
    Otherwise, returns False.
    """
    for op in all_ops:
        if op in string:
            return op
    return False

def combineTimestampTokens(array):
    """
    Check to see whether there are consecutive tokens consisting of a
    timestamp of the form "YYYY-MM-DD", "HH:MM:SS" and if there are, then
    the two are regenerated to form one single token, with date and time
    together.
    """
    # Need to use a while loop because we're removing elements from the
    # array
    i = 0
    while i < len(array):
        if date_regexp.match(array[i]) and time_regexp.match(array[i+1]):
            # Combine the date (array[i]) and time (array[i+1]) tokens
            # and place them in array[i], and delete the now-extraneous
            # token at array[i+1].
            array[i] = array[i] + " " + array[i+1]
            del array[i+1]
        i += 1
    return array

def execute_query(query):
    """
    Tries to run the given query using the given database connection.

    db is a DB connection (of any type), and the query is the (string)
    representation of the query to execute. Returns None if no rows are
    in the result set, True otherwise.
    If an Exception is raised when running cursor.execute, this function
    will explicitly not catch it.
    """
    global result_rows
    global cursor
    global meta_dict
    global column_names

    # Re-initialize since this is called every time we do Query#lshift
    # or Query#rshift
    result_rows = None
    cursor = None
    meta_dict = {}
    column_names = None

    cursor = quest.engine.run_sql(query)
    result_rows = cursor.fetchall()

    if len(result_rows) == 0:
        # No results
        return None
    else:
        first_row = result_rows[0]
        # cursor.description[i] is like
        # ('playerID', None, None, None, None, None, None)
        column_names = [d[0] for d in cursor.description]

        for index, value in enumerate(first_row):
            # Map a column name to its type (e.g. int)
            # meta_dict["movie_id"] = int
            column_name = column_names[index]
            column_type = type(value)
            meta_dict[column_name] = column_type
        return True

def column_index(column_name):
    """
    Returns index of column with given name in result_rows, or None
    if no column in result_rows has the given name.
    """
    try:
        return column_names.index(column_name)
    except ValueError:
        # No column with this name exists
        return None

def shift(attr_name, attr_value, shift_type):
    """
    Shift attribute with given name and value according to
    shift_type.

    Raises a TypeError if shift_type does not equal either of the magic
    constants LSHIFT or RSHIFT.
    """
    if shift_type not in [LSHIFT, RSHIFT]:
        raise TypeError("Incorrect shift_type (%s), must provide LSHIFT or RSHIFT." % shift_type)

    numeric_types = (int, float, long)
    attr_type = meta_dict[attr_name]

    if attr_type in numeric_types:
        # A number of some sort.
        if shift_type == RSHIFT:
            return str(attr_type(attr_value)+1)
        else:
            return str(attr_type(attr_value)-1)

    elif attr_type == datetime.timedelta:
        attr_value = attr_value.split("'")[1]
        time_segment = attr_value.split(":")
        hours, minutes, seconds = [int(t) for t in time_segment]

        base_time = datetime.timedelta(seconds = seconds, minutes = minutes, hours = hours)
        time_shift_amount = datetime.timedelta(seconds = 1)

        if shift_type == RSHIFT:
            final_time = str(base_time + time_shift_amount).split()
            return "'%s'" % final_time[-1]
        else:
            final_time = str(base_time - time_shift_amount).split()
            return "'%s'" % final_time[-1]

    elif attr_type == datetime.date:
        # A date, with or without a time
        attr_value = attr_value.split("'")[1]

        if date_regexp.match(attr_value):
            # Set variables outside the if so they have non-local scope
            base_date = None
            time_shift_amount = None

            if time_regexp.match(attr_value):
                # This is a date and time, so shift by 1 second forward or back
                time_shift_amount = datetime.timedelta(seconds = 1)

                date_segment = attr_value.split()[0].split("-")
                time_segment = attr_value.split()[1].split(":")

                year, month, day = [int(t) for t in date_segment]
                hour, minute, second = [int(t) for t in time_segment]

                base_date = datetime.datetime(year, month, day, hour, minute, second)
            else:
                # This is a date (without a time), so shift by 1 day forward or back
                time_shift_amount = datetime.timedelta(days = 1)
                date = attr_value.split('-')
                year, month, day = [int(t) for t in date]
                base_date = datetime.date(year, month, day)

            if base_date is None or time_shift_amount is None:
                # Couldn't shift
                return attr_value
            else:
                if shift_type == RSHIFT:
                    return "'%s'"% (base_date + time_shift_amount)
                else:
                    return "'%s'"% (base_date - time_shift_amount)

    elif attr_type in (str, unicode):
        # attr is a string of some sort.
        match = rBareAttribute.match(attr_value)
        # Set outside the if so it has wider scope
        # bare_attr_value is the attr without enclosing quotes or table
        # references
        bare_attr_value = None
        if match:
            bare_attr_value = match.groups(1)
        else:
            # FIXME: no attribute found, error
            pass

        # attr is the attr_index'th column
        attr_index = column_index(bare_attr_value)
        if attr_index is None:
            # Not a valid column name, don't shift.
            return attr_value
        else:
            # rows_sorted_by_attr_value is a copy of result_rows, with each row sorted by
            # the value of its attr_index'th column, which is the column
            # corresponding to the attr we're shifting.
            rows_sorted_by_attr_value = sorted(result_rows, key = itemgetter(attr_index))
            # data_index is the index in rows_sorted_by_attr_value of
            # the row containing attr_value for the given column
            data_index = 0
            for index, row in enumerate(rows_sorted_by_attr_value):
                if bare_attr_value == row[attr_index]:
                    data_index = index
                    break

            if shift_type == RSHIFT:
                if data_index < len(result_rows)-1:
                    # We can RSHIFT, do so.
                    # data_index is where we found the attribute, so return
                    # the next item that's actually in the sorted rows
                    # (e.g. "David" is in the DB, and so is "Eric", and
                    # "Eric" is the next-highest value after "David", so
                    # we return "Eric")
                    return "'%s'" % rows_sorted_by_attr_value[data_index+1][attr_index]
                else:
                    # We can't RSHIFT, return the unshifted value.
                    print "End of data set! RSHIFT not performed."
                    return attr_value

            else:
                if data_index > 0:
                    # We can LSHIFT, do so.
                    return "'%s'" % rows_sorted_by_attr_value[data_index-1][attr_index]
                else:
                    # We can't LSHIFT, return the unshifted value.
                    print "End of data set! LSHIFT not performed."
                    return attr_value

    # Something happened, we couldn't shift at all. Return unshifted
    # value.
    return attr_value

def parseStringAndShift(query, att, shift_type):
    """
    Parses the given query and shifts its <att> attribute according
    to shift_type. shift_type is either LSHIFT or RSHIFT.
    """

    att = att.strip()

    # Remove repeated whitespace
    sanitized_query = rWhitespace.sub(' ', query)
    sanitized_query = re.sub(r';$', '', sanitized_query)
    query_array_with_combined_timestamps = combineTimestampTokens(rChunker.split(sanitized_query))
    # Remove extra whitespace tokens from query array
    split_query = ' '.join(query_array_with_combined_timestamps).split()

    # Was the previous clause WHERE or HAVING?
    found_where_or_having = False

    # Keep track of our index in the query string as we parse through it.
    i = 0

    # Did we shift at all?
    did_shift = False

    while i < len(split_query):
        token = split_query[i].strip()
        if token.lower() in ('where', 'having'):
            found_where_or_having = True
            next
        if not found_where_or_having:
            # Haven't found WHERE or HAVING yet, keep going.
            next

        if att in token and findOperator(token):
            # "att< 3" (i.e. no space between attribute and operator)
            # or
            # "att< 'string'"

            # Rewrite the query so that the attribute and operator are
            # separate tokens, and let the other if statements handle
            # the rewritten query
            operator = findOperator(token)
            tokens = rOperator.split(token)
            # "att<" becomes "att", "<", i.e. separate tokens
            split_query[i] = att
            split_query.insert(i+1, operator)
            # Let other pieces of code handle the rewritten query
            next

        elif att == token and findOperator(split_query[i+1]) and ("'" in split_query[i+2] or split_query[i+2].isdigit()):
            # "att > 3" (i.e. space between attribute and operator)
            # or
            # "att > 'string'"

            did_shift = True
            operator = findOperator(split_query[i+1])
            tokens = rOperator.split(split_query[i+1])

            if tokens[-1] == '':
                # FIXME: why check for an empty string here?
                value = split_query[i+2]
                new_value = shift(att, value, shift_type)
                # end up with "att > 4", using the example above
                split_query[i] = att
                split_query[i+1] = operator
                split_query[i+2] = new_value
                i += 2

            else:
                value = tokens[-1]
                new_value = shift(att, value, shift_type)
                split_query[i] = att
                split_query[i+1] = operator + new_value
                i += 1

        elif token == att and [s.lower() for s in split_query[i:i+2]] == ['not', 'between']:
            # "x NOT BETWEEN l_value AND r_value"
            did_shift = True

            l_value = split_query[i+3]
            r_value = split_query[i+5]

            new_l_value = shift(att, l_value, shift_type)
            new_r_value = shift(att, r_value, shift_type)
            # change l_value and r_value to new_l_value and
            # new_r_value, respectively
            split_query[i+3] = new_l_value
            split_query[i+5] = new_r_value
            i += 5

        elif token == att and split_query[i+1].lower() == 'between':
            # "x BETWEEN l_value AND r_value"
            did_shift = True

            l_value = split_query[i+2]
            r_value = split_query[i+4]
            new_l_value = shift(att, l_value, shift_type)
            new_r_value = shift(att, r_value, shift_type)

            # change l_value and r_value to new_l_value and
            # new_r_value, respectively
            split_query[i+2] = new_l_value
            split_query[i+4] = new_r_value
            i += 4

        elif token == att and split_query[i+1].lower() == 'in' and ("'" in split_query[i+3] or split_query[i+3].isdigit()):
            # "att IN 'string'
            # or
            # "att IN (3,4,5)"
            did_shift = True

            # For "(3,4,5)", set i to the first index after the "(" and
            # iterate until we hit the ending ")"
            i += 3
            while split_query[i] != ')':
                split_query[i] = shift(att, split_query[i], shift_type)
                i += 2

        elif token == att and [s.lower() for s in split_query[i:i+2]] == ['not', 'in'] and ("'" in split_query[i+4] or split_query[i+4].isdigit()):
            # "att NOT IN 'string'
            # or
            # "att NOT IN (3,4,5)"
            did_shift = True

            i += 4
            while split_query[i] != ')':
                split_query[i] = shift(att, split_query[j], shift_type)
                i += 2

        elif token == att and split_query[i+1].lower() == 'like':
            # "att LIKE comparison"
            did_shift = True

            comparison = split_query[i+2]
            split_query[i+2] = shift(att, comparison, shift_type)
            i += 2

        elif token == att and [s.lower() for s in split_query[i:i+2]] == ['not', 'like']:
            # "att NOT LIKE comparison"
            did_shift = True

            comparison = split_query[i+3]
            split_query[i+3] = shift(att, comparison, shift_type)
            i += 3

        elif token == att and split_query[i+1] == ')' and findOperator(split_query[i+2]):
            # "att ) <operator> operand"
            did_shift = True

            operand = split_query[i+3]
            split_query[i+3] = shift(att, operand, shift_type)
            i += 3
        i += 1

    if not did_shift:
        err_msg = "Didn't shift: attribute %s not found in supplied query." % att
        raise DidNotShiftException(err_msg)
    else:
        final_query = ' '.join(split_query)
        return final_query

def rshift(query, attribute):
    """Convenience method."""
    # Need to run execute_query first
    execute_query(query)
    return parseStringAndShift(str(query), attribute, RSHIFT)

def lshift(query, attribute):
    """Convenience method."""
    # Need to run execute_query first
    execute_query(query)
    return parseStringAndShift(str(query), attribute, LSHIFT)

def test_mysql(attribute = 'throws', shift_type = LSHIFT):
    """Test on MySQL database."""

    mysql_db = MySQLdb.connect(host = "localhost", user = "root", passwd = "bergstrom", db = "baseball")
    mysql_query = 'select throws from playerStats'
    mysql_query = 'select * from playerStats where %s between 0 and 8000' % attribute
    print mysql_query
    result = execute_query(mysql_db, mysql_query)
    #print result_rows
    if result is None:
        print "No results returned, not shifting."
        return None
    else:
        print meta_dict
        print parseStringAndShift(mysql_query, attribute, shift_type)

if __name__ == "__main__":
    test_mysql()
