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

    def __init__(self,
            banner='Welcome to Quest! For help, type "help" and hit RETURN.',
            histfile=os.path.expanduser("~/.quest_history")):
        """Calls init_history()."""
        self.banner = banner
        self.init_history(histfile)
        self.engine = quest.engine

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
            quest_command_match = re.match(self.rQuestCommand, answer)
            if sql_match:
                # Answer is pure SQL
                print "** SQL DETECTED **"
                return self.engine.run_sql(answer)
            elif quest_commmand_match:
                # Answer is a Quest operator, delegate
                print "** QUEST OPERATOR DETECTED **"
                query_variable = quest_command_match.group(1)
                quest_operator = quest_command_match.group(2)
                arguments = quest_command_match.group(3)

                # Initialize to None in case we fail to set a valid +query+ below
                query = None

                if query_variable is not None:
                    # User is calling an operator on a specific query.
                    # Try to look up the query in the query cache.
                    try:
                        query = query_cache.get(query_variable)
                    except KeyError:
                        # Pass because we print an error message later.
                        pass
                else:
                    # No query variable specified, so use most recent query
                    query = query_cache.most_recent_query()

                if query is None:
                    # Either we failed to get query_variable from query cache, or
                    # this is the first command (so most_recent_query is None).
                    # In any case, fail.
                    print "!!!", query_variable, # note ending comma
                    print "is not a valid query variable. Please try again."
                else:
                    # We have a query.
                    if arguments is None:
                        print "You must provide arguments to", operator
                        print "Please use this syntax:",
                        "[<query variable>.]{}(arg1, arg2, ...)".format(operator)
                    else:
                        try:
                            # query_function is e.g. query.narrow
                            query_function = getattr(query, operator.lower())
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
                            query_cache.put(None, new_query)
                            return new_query
            else:
                print "ERR: {} is not valid SQL or a Quest operator. Please try again.".format(answer)
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
