import readline
import atexit
import os
import re

import quest.engine
from quest.query import query_cache

class Prompt:
    """A basic REPL (read-eval-print-loop) that passes user input to the Quest engine.

    It accepts pure SQL or Quest-specific operators.
    It shows an error message (but doesn't raise an error) on invalid input.
    To quit: type "exit" or "exit()" and hit ENTER, or hit Ctrl-D (EOF).
    """
    # Some class-level regexps
    rSql = re.compile(r"^(select|update|insert) .+", re.IGNORECASE)

    # Quest-specific operators
    # Matches a line with a Quest operator, regardless of case.
    # So Q.rollup(predicate) would match, as would rollup(predicate).
    # Groups:
    #  1: the query variable (e.g. Q)
    #  2: the operator name
    #  3: the arguments (arguments aren't optional, but we make an optional match
    #     here so we can check if they're None later).
    rQuestOperator = re.compile(r"^(.*\.)(rollup|drilldown|store|relax|narrow)(?:\((.+)\))?",
            re.IGNORECASE)

    def __init__(self,
            banner='Welcome to Quest! For help, type "help" and hit RETURN.',
            histfile=os.path.expanduser("~/.quest_history")):
        """Calls init_history()."""
        self.banner = banner
        self.init_history(histfile)
        self.engine = quest.engine.engine_instance

    def interact(self, prompt=">>> "):
        """Starts up the REPL, prints banner message and passes user input to handle_answer."""
        print self.banner
        handle_value = None
        quit_words = ["exit", "exit()", "quit", "quit()"]
        while handle_value not in quit_words:
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
        print "Quest: QUery Engine for Selecting Tables"
        print "SQL: You can type in any valid SQL expression to see its result."
        print "You can also use some Quest-specific operators:"
        print "\trollup(Q): rolls up a query Q"
        print "\tdrilldown(Q): drilldown on a query Q"
        print "\t" + 'relax(Q, r): "OR" the select clause of Q with predicate r'
        print "\t" + 'narrow(Q, r): "AND" the select clause of Q with predicate r'

    def handle_answer(self, answer):
        """Handle user input; called by interact()."""
        answer = answer.strip()
        if answer.lower() == "help" or answer.lower() == "help()":
            self.help()
        elif answer.lower() == "exit" or answer.lower() == "exit()":
            return "exit"
        elif answer == "":
            print "Please enter something other than whitespace."
        else:
            sql_match = re.match(self.rSql, answer)
            quest_operator_match = re.match(self.rQuestOperator, answer)
            if sql_match:
                # Answer is pure SQL
                print "** SQL DETECTED **"
                # Tell quest to run pure SQL
                return self.engine.run_sql(answer)
            elif quest_operator_match:
                # Answer is a Quest operator, delegate
                print "** QUEST OPERATOR DETECTED **"
                query_variable = quest_operator_match.group(1)
                quest_operator = quest_operator_match.group(2)
                arguments = quest_operator_match.group(3)

                if query_variable is not None:
                    # User is calling an operator on a specific query
                    # Try to look up the query in the query cache
                    query = query_cache.get(query_variable)
                else:
                    # No query variable specified, so use most recent query
                    query = query_cache.most_recent_query()

                if query is None:
                    # Either failed to get query_variable from query cache, or
                    # this is the first command (so most_recent_query is None).
                    # Either way, fail.
                    print "!!!", query_variable, "is not a valid query variable!"
                    return False
                else:
                    # We have a query.
                    if arguments is None:
                        print "Please provide arguments to", operator
                        return False
                    else:
                        try:
                            # e.g. query.narrow
                            query_function = getattr(query, operator.lower())
                            return_value = query_function(*arguments)
                            print return_value
                            return return_value
                        except TypeError as te:
                            print te
                            return False
            else:
                print "ERR: {} is not valid SQL or a Quest operator. Please try again.".format(answer)

    def init_history(self, histfile):
        """Initialize the history management.

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
