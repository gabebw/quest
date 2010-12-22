# Handle user input from any source (i.e. provided by command-line
# prompt or Web interface).

import re

import quest.engine
from quest.query import query_cache
import quest.config as config

# Returned by handle() when user indicated they want to quit
QUIT = "quit"

rSql = re.compile(r"^(select|update|insert) .+", re.IGNORECASE)

# Quest-specific operators
rQuestOperator = r"\.(rollup|drilldown|store|relax|narrow|relate|show|rshift|lshift)"
rInitialize = re.compile(r"initialize\(\s*(.+?)\s*,\s*(.+)\s*\)", re.IGNORECASE)
# A query variable has to be word characters, so "my_query_variable" works
# but "so awesome!!" doesn't. The query variable is optional; if the user
# just types "rollup(<predicate>)", we use the most recent query.
rQueryVariable = r"^(?:\s*(\w+))?"
# Even though arguments aren't syntactically optional, we make this is an
# optional match so that we can check for "arguments == None" later.
rArguments = r"(?:\s*\((.+)\s*\))?"
# Matches a line with a Quest operator, regardless of case.
# So Q.rollup(predicate) would match, as would rollup(predicate).
# Groups:
#  1: the query variable (e.g. "Q", or None in the second example)
#  2: the operator name  (e.g. "rollup")
#  3: the arguments      (e.g. "predicate")
rQuestCommand = re.compile(rQueryVariable + rQuestOperator + rArguments,
        re.IGNORECASE)
# Just a variable, no operator
rBareVariable = re.compile(rQueryVariable + "$", re.I)

# If the user enters commands like "q.rollup(X)", we use this to
# remove the quotes
rBeginOrEndQuotes = re.compile(r"^['\"]|['\"]$")

def help():
    """Print the help."""
    return """
    Quest: QUery Engine for Selecting Tables
    \tSQL: You can type in any valid SQL expression to see its result.
    You can also use some Quest-specific operators. Note that the
    "Q." is optional; if you don't specify a query to perform a
    Quest operation on, the most recent query will be used. Also note
    that the query is (usually) not sent to the database until show() is
    called, though there are config settings in config.py that can
    change this.
    \t[Q.]rollup(attr): rolls up on a query Q on given attribute
    \t[Q.]drilldown(attr): drills down on a query Q on given attribute
    \t[Q.]relax(pred): "OR" the select clause of Q with given predicate
    \t[Q.]narrow(pred): "AND" the select clause of Q with given predicate
    \t[Q.]relate(other_query): Perform a natural join with other_query
    \t[Q.]store(table_name): Store the result of running Q in a table with the given name.
    \t[Q.]show(): Actually send the query Q to the database and print the result.
    """.strip()

def handle(user_input):
    """Handle user input."""
    # Change '"I am some text"' to 'I am some text'
    user_input = rBeginOrEndQuotes.sub('', user_input).strip()
    quit_words = ["exit", "exit()", "quit", "quit()"]
    help_words = ["help", "help()"]
    if user_input.lower() in help_words:
        return help()
    elif user_input.lower() in quit_words:
        return QUIT
    elif user_input == "":
        return "Please enter something other than whitespace."
    else:
        sql_match = re.match(rSql, user_input)
        initialize_match = re.match(rInitialize, user_input)
        # Sometimes the user enters just "Q"
        bare_variable_match = re.match(rBareVariable, user_input)
        quest_command_match = re.match(rQuestCommand, user_input)

        if sql_match:
            # user_input is pure SQL
            #print "** SQL DETECTED **"
            try:
                cursor = quest.engine.run_sql(user_input)
            except Exception, e:
                # Re-raise exception
                raise e

            # rowcount is -1 or None if no query was run or number
            # of rows can't be determined
            if cursor.rowcount and cursor.rowcount > 0:
                # TODO: warn if >20 rows?
                return cursor.fetchall()
            else:
                # Something went wrong, but didn't raise an error.
                # Very peculiar, and probably shouldn't happen.
                return "!!! Something went wrong: %s" % cursor.info
        elif initialize_match:
            #print "** INITIALIZE OPERATOR DETECTED **"
            # Strip quotes, in case people do something like
            # `INITIALIZE("Q", "SELECT * FROM table")`
            query_variable = rBeginOrEndQuotes.sub('', initialize_match.group(1))
            sql = rBeginOrEndQuotes.sub('', initialize_match.group(2))
            query_cache.put(query_variable, sql)
            return "Initialized %s to %s" % (query_variable, sql)
        elif bare_variable_match:
            # User entered just a Quest variable, sans operator
            user_query_variable = bare_variable_match.group(1)
            try:
                query_key, query = extract_query_key_and_query(user_query_variable)
                return str(query)
            except Exception, e:
                return str(e)
        elif quest_command_match:
            # User entered a Quest variable, with an operator
            # user_input is a Quest operator, delegate
            user_query_variable = quest_command_match.group(1)
            quest_operator = quest_command_match.group(2)

            # Initialize to None in case we fail to set a valid +query+ below
            query = None
            # a key in query_cache.cache that is associated with a
            # Query instance
            query_key = None

            try:
                query_key, query = extract_query_key_and_query(user_query_variable)
            except Exception, e:
                return str(e)

            if query is None:
                if user_query_variable is None and query_key is None:
                    # User hasn't called INITIALIZE yet - they
                    # didn't provide a query variable, and we
                    # couldn't get one from the cache
                    return "!!! Please run INITIALIZE(<variable>, <SQL query>)"
                else:
                    return False
            else:
                if not quest_operator:
                    # Just a query variable, no operator.
                    return str(query)
                else:
                    # We have a query, with operators.
                    if quest_operator.lower() == "show":
                        # Special handling because show can take 0 arguments
                        arguments = quest_command_match.group(3)
                        if arguments is None:
                            return query.show()
                        else:
                            arguments = [rBeginOrEndQuotes.sub('', str(arg).strip()) for arg in arguments.split(',')]
                            # Only take the first argument
                            return query.show(arguments[0])
                    else:
                        arguments = quest_command_match.group(3)
                        if arguments is None:
                            err_msg = "You must provide arguments to %s" % quest_operator
                            err_msg += "\nPlease use this syntax:"
                            err_msg += "[<query variable>.]%s(arg1, arg2, ...)" % quest_operator
                            return err_msg
                        else:
                            # Turn "'foo', bar" into ["foo", "bar"]
                            arguments = [rBeginOrEndQuotes.sub('', str(arg).strip()) for arg in arguments.split(',')]
                            try:
                                # query_function is e.g. query.narrow
                                query_function = getattr(query, quest_operator.lower())
                            except TypeError, te:
                                raise te
                            new_query = query_function(*arguments)
                            returned_string = ""
                            if quest_operator.lower() == 'store':
                                # Don't save the query
                                returned_string += "Ran this SQL: %s" % new_query
                            else:
                                returned_string += "New query: %s" % new_query
                                # Give the new query a unique name and put it in the
                                # query cache.
                                key, query = query_cache.put(None, new_query)
                                returned_string += "\n** New query put in cache as %s" % key
                                if should_show_query():
                                    rows = new_query.show()
                                    returned_string += "\n" + str(rows)
                            return returned_string
        else:
            return "ERR: %s is not valid SQL or a Quest operator. Please try again." % user_input
        # If we haven't returned by now, it's an error. Return False.
        return False

def should_show_query():
    """
    Returns True if Quest is configured to always SHOW a query, even
    without user explicitly asking for it, False otherwise.
    """
    return config.ALWAYS_SHOW is True

def extract_query_key_and_query(variable):
    """
    Given a variable like "Q", get the query key ("Q") and the
    associated query instance from the cache. If variable is None, then
    gets the most recent query and its key from the cache.

    Returns a tuple of (key, query_instance), or raises an Exception.
    """

    if variable is None:
        # No query variable specified, so use most recent query
        query_key, query = query_cache.most_recent_key_and_query
        return (query_key, query)
    else:
        # User is calling an operator on a specific query.
        # Try to look up the query in the query cache.
        query_key = variable
        try:
            query = query_cache.get(query_key)
            return (query_key, query)
        except KeyError:
            # User is trying to use a non-initialized
            # variable
            raise Exception("!!! %s is not a valid query variable. Please try again." % variable)
