# Install via "pip install sqlparse", or if you don't have pip, via
# "easy_install sqlparse".
import sqlparse

def lex(query):
    """Pass in a query as a string, and it will return the parsed tokens
    of that string.
    """
    # parsed is an N-element tuple containing each separate statement in
    # a given query. Since we're feeding it single-statement queries,
    # it's a 1-element tuple in these cases, so return the first
    # element.
    parsed = sqlparse.parse(query)
    return parsed[0]
