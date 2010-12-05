import sqlparse
import re

import quest.engine

rFrom = re.compile("from", re.IGNORECASE)

def materialize(query, new_table_name):
    """
    Performs query and stores the result in a table with the given
    name (in the current DB).

    Returns the result of running quest.engine.run_sql().
    """
    parsed = sqlparse.parse(query)
    new_query = ""
    # Only replace FROM once
    did_replace = False
    for statement in parsed:
        for token in statement.tokens:
            # "SELECT * FROM table"
            # becomes
            # "SELECT INTO temp_table FROM table"

            if not did_replace:
                # Only replace once
                replace_string = 'INTO ' + new_table_name + ' FROM'
                token = rFrom.sub(replace_string, str(token))
                did_replace = True
            new_query += str(token)

    quest.engine.run_sql(new_query)
