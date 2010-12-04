import readline
import atexit
import os
import re

import quest.engine
from quest.query import query_cache
import quest.config as config

class Prompt:
    """
    A basic REPL (read-eval-print-loop) that passes user input to the Quest engine.

    It accepts pure SQL or Quest-specific operators.
    It shows an error message (but doesn't raise an error) on invalid input.
    To quit: type "exit" or "exit()" and hit ENTER, or hit Ctrl-D (EOF).
    """
    # Some class-level regexps
    rSql = re.compile(r"^(select|update|insert) .+", re.IGNORECASE)

    # Quest-specific operators
    rQuestOperator =r"(rollup|drilldown|store|relax|narrow|relate)"
    rInitialize = re.compile(r"initialize\((.+), (.+)\)", re.IGNORECASE)
    # A query variable has to be word characters, so "my_query_variable" works
    # but "so awesome!!" doesn't. The query variable is optional; if the user
    # just types "rollup(<predicate>)", we use the most recent query.
    rQueryVariable = r"^(?:(\w+)\.)?"
    # Even though arguments aren't syntactically optional, we make this is an
    # optional match so that we can check for "arguments == None" later.
    rArguments = r"(?:\((.+)\))?"
    # Matches a line with a Quest operator, regardless of case.
    # So Q.rollup(predicate) would match, as would rollup(predicate).
    # Groups:
    #  1: the query variable (e.g. "Q", or None in the second example)
    #  2: the operator name  (e.g. "rollup")
    #  3: the arguments      (e.g. "predicate")
    rQuestCommand = re.compile(rQueryVariable + rQuestOperator + rArguments,
            re.IGNORECASE)


    # If the user enters commands like "q.rollup(X)", we use this to
    # remove the quotes
    rBeginOrEndQuotes = re.compile(r"^['\"]|['\"]$")

    def __init__(self,
            banner='Welcome to Quest! For help, type "help" and hit RETURN.',
            histfile=os.path.expanduser("~/.quest_history")):
        """Calls init_history()."""
        self.banner = banner
        self.init_history(histfile)

    def interact(self, prompt=">>> "):
        """Starts up the REPL, prints banner message and passes user input to handle_answer."""
        print self.banner
        handle_value = None
        # handle_answer returns "exit" when user wants to exit.
        while handle_value != "exit":
            try:
                answer = self.get_input(prompt)
            except EOFError:
                # User hit Ctrl-D, quit.
                print # get on a newline first
                break
            handle_value = self.handle_answer(answer)
        print "Bye!"

    def get_input(self, prompt):
        """Prompts for user input using given prompt string and returns input."""
        text = raw_input(prompt)
        # Change '"I am some text"' to 'I am some text'
        text = rBeginOrEndQuotes.sub('', text)
        return text

    def help(self):
        """Print the help."""
        print """
        Quest: QUery Engine for Selecting Tables
        SQL: You can type in any valid SQL expression to see its result.
        You can also use some Quest-specific operators. Note that the
        "Q." is optional; if you don't specify a query to perform a
        Quest operation on, the most recent query will be used.
        \t[Q.]rollup(attr): rolls up on a query Q on given attribute
        \t[Q.]drilldown(attr): drills down on a query Q on given attribute
        \t[Q.]relax(pred): "OR" the select clause of Q with given predicate
        \t[Q.]narrow(pred): "AND" the select clause of Q with given predicate
        \t[Q.]relate(other_query): Perform a natural join with other_query
        \t[Q.]store(table_name): Store the result of running Q in a table with the given name.
        """

    def handle_answer(self, answer):
        """Handle user input. Called by interact()."""
        answer = answer.strip()
        quit_words = ["exit", "exit()", "quit", "quit()"]
        help_words = ["help", "help()"]
        if answer.lower() in help_words:
            self.help()
        elif answer.lower() in quit_words:
            return "exit"
        elif answer == "":
            print "Please enter something other than whitespace."
        else:
            sql_match = re.match(self.rSql, answer)
            initialize_match = re.match(self.rInitialize, answer)
            quest_command_match = re.match(self.rQuestCommand, answer)

            if sql_match:
                # Answer is pure SQL
                print "** SQL DETECTED **"
                try:
                    cursor = quest.engine.run_sql(answer)
                except Exception as e:
                    print e
                    return False

                # rowcount is -1 or None if no query was run or number
                # of rows can't be determined
                if cursor.rowcount and cursor.rowcount > 0:
                    # TODO: warn if >20 rows?
                    for row in cursor.fetchall():
                        print row
                else:
                    # Something went wrong, but didn't raise an error.
                    # Very peculiar, and probably shouldn't happen.
                    print "!!! Something went wrong: %s" % cursor.info
            elif initialize_match:
                print "** INITIALIZE OPERATOR DETECTED **"
                # Strip quotes, in case people do something like
                # `INITIALIZE("Q", "SELECT * FROM table")`
                query_variable = rBeginOrEndQuotes.sub('', initialize_match.group(1))
                sql = rBeginOrEndQuotes.sub('', initialize_match.group(2))
                query_cache.put(query_variable, sql)
                print "Initialized", query_variable, "to", sql

            elif quest_command_match:
                # Answer is a Quest operator, delegate
                print "** QUEST OPERATOR DETECTED **"
                user_query_variable = quest_command_match.group(1)
                quest_operator = quest_command_match.group(2)
                arguments = quest_command_match.group(3)

                # Initialize to None in case we fail to set a valid +query+ below
                query = None
                # a key in query_cache.cache that is associated with a
                # Query instance
                query_key = None

                if user_query_variable is not None:
                    # User is calling an operator on a specific query.
                    # Try to look up the query in the query cache.
                    query_key = user_query_variable
                    try:
                        query = query_cache.get(query_key)
                    except KeyError:
                        # User is trying to use a non-initialized
                        # variable
                        print "!!!", user_query_variable, # note ending comma
                        print "is not a valid query variable. Please try again."
                        return False
                else:
                    # No query variable specified, so use most recent query
                    query_key, query = query_cache.most_recent_key_and_query

                if query is None:
                    if user_query_variable is None and query_key is None:
                        # User hasn't called INITIALIZE yet - they
                        # didn't provide a query variable, and we
                        # couldn't get one from the cache
                        print "!!! Please run INITIALIZE(<variable>, <SQL query>)"
                    return False
                else:
                    # We have a query.
                    if arguments is None:
                        print "You must provide arguments to", quest_operator
                        print "Please use this syntax:",
                        "[<query variable>.]%s(arg1, arg2, ...)" % quest_operator
                    else:
                        try:
                            # query_function is e.g. query.narrow
                            query_function = getattr(query, quest_operator.lower())
                        except TypeError as te:
                            print te
                        else:
                            new_query = query_function(*arguments)
                            if self.should_show_query():
                                rows = new_query.show()
                                print rows
                            print new_query
                            # Give the new query a unique name and put it in the
                            # query cache.
                            key, query = query_cache.put(None, new_query)
                            print "Query put in cache as", key
                            return new_query
            else:
                print "ERR: %s is not valid SQL or a Quest operator. Please try again." % answer
            # If we haven't returned by now, it's an error. Return False.
            return False

    def should_show_query(self):
        """
        Returns True if Quest is configured to always SHOW a query, even
        without user explicitly asking for it, False otherwise.
        """
        return config.ALWAYS_SHOW is True

    def init_history(self, histfile):
        """
        Initialize the history management.

        Reads histfile and registers save_history() to run atexit. Prints an
        error message if it fails.
        """
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                print "Couldn't read history file!"
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        """Saves readline history in histfile. Prints an error message if it fails."""
        try:
            readline.write_history_file(histfile)
        except:
            print "ERROR: Couldn't write history file", histfile
