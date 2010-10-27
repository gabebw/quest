import readline
import atexit
import os
import re

import quest.backend.engine

class Prompt:
    """A basic REPL (read-eval-print-loop) that passes user input to the Quest engine.

    It accepts pure SQL or Quest-specific operators.
    Currently, it only pretty-prints what the user types in, with a note as to
    whether it's SQL or a Quest operator. It shows an error message (but doesn't
    raise an error) on invalid input.
    To quit: type "exit" or type "exit()" and hit ENTER, or hit Ctrl-D (EOF).
    """
    # Some class-level regexps
    rSql = re.compile(r"^(select|update|insert) .+", re.IGNORECASE)

    # Quest-specific operators
    # Matches a line starting with a Quest operator, regardless of case.
    rQuestOperator = re.compile(r"^(rollup|drilldown|store|relax|narrow)",
            re.IGNORECASE)
   
    def __init__(self,
            banner='Welcome to Quest! For help, type "help" and hit RETURN.',
            histfile=os.path.expanduser("~/.quest_history")):
        """Calls init_history()."""
        self.banner = banner
        self.init_history(histfile)
        self.engine = quest.backend.engine.Engine()

    def interact(self, prompt=">>> "):
        """Starts up the REPL, prints banner message and passes user input to handle_answer."""
        print self.banner
        handle_value = None
        while handle_value != "exit":
            try:
                answer = self.get_input(prompt)
            except EOFError:
                # User hit Ctrl-D, quit.
                print "\nBye!" # get on a newline first
                break
            handle_value = self.handle_answer(answer)

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
                operator = quest_operator_match.group(1)
                # We have an operator, now get the arguments
                answer_without_operator = answer.replace(operator, '', 1)
                if answer_without_operator == '':
                    print "Please provide arguments to", operator
                if answer_without_operator[0] == '(' and answer_without_operator[-1] == ')':
                    arguments = answer_without_operator[1:-1].split(", ")
                    try:
                        return self.engine.apply_operator(operator.lower(), *arguments)
                    except TypeError as te:
                        print te
                        return False
                else:
                    print "Please use this syntax: {}(<arguments...>)".format(operator)
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
