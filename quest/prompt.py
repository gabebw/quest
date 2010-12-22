import readline
import atexit
import os
import re

from quest import input_handler

class Prompt:
    """
    A basic REPL (read-eval-print-loop) that passes user input to the Quest engine.

    It accepts pure SQL or Quest-specific operators.
    It shows an error message (but doesn't raise an error) on invalid input.
    To quit: type "exit" or "exit()" and hit ENTER, or hit Ctrl-D (EOF).
    """

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
        # input_handler.handle() returns input_handler.QUIT when user wants to exit.
        while handle_value != input_handler.QUIT:
            try:
                answer = self.get_input(prompt)
            except EOFError:
                # User hit Ctrl-D, quit.
                print # get on a newline first
                break
            try:
                handle_value = input_handler.handle(answer)
            except Exception, e:
                # Catch everything
                print e
            else:
                if handle_value != input_handler.QUIT:
                    print handle_value

        print "Bye!"

    def get_input(self, prompt):
        """Prompts for user input using given prompt string and returns input."""
        text = raw_input(prompt)
        # Change '"I am some text"' to 'I am some text'
        text = self.rBeginOrEndQuotes.sub('', text)
        return text

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
