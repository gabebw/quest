"""
The actual engine that ties the whole backend together. Delegates a lot of stuff
to quest.*.
"""

from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text

import quest.operators
import quest.config

class Engine:
    def __init__(self):
        self.queries = []
        # in-memory SQLite engine
        self.sql_engine = create_engine('sqlite:///:memory:', echo=True)
        self.connection = self.sql_engine.connect()

    def most_recent_query(self):
        """Return the most recent query, or None if empty.."""
        try:
            return self.queries[-1]
        except IndexError:
            return None

    def run_sql(self, sql):
        """Evaluates a pure SQL expression. Currently just prints it."""
        t = text(answer)
        print t
        # TODO: should this be translated to SQLAlchemy first?
        self.queries.append(t)
        return self.connection.execute(t)

    def apply_operator(self, operator_name, query, predicate):
        """Apply the given operator_name to the query using the given predicate.

        Appends the result to self.queries and returns the new query.
        operator_name should exist in quest.operators. If it doesn't, then
        prints an AttributeError and returns False.
        For more on what each operator does, see operators/<operator_name>.py.
        """

        operator_name = operator_name.lower()
        # The show operator is actually a part of the engine
        if operator_name == 'show':
            self.show(query, number_of_rows = predicate)
        else:
            # Get the function, e.g. quest.operators.drilldown
            try:
                operator = getattr(quest.operators, operator_name)
            except AttributeError as ae:
                print ae
                return False
            else:
                new_query = operator(query, predicate)
                self.queries.append(new_query)
                # Show the query, but don't put it in self.queries since they
                # didn't actually call SHOW
                if quest.config.show_behavior == quest.config.SHOW_ALL:
                    self.show(new_query)
                elif quest.config.show_behavior == quest.config.SHOW_N:
                    self.show(new_query, quest.config.number_of_rows_to_show)
                return new_query

    def show(self, query, number_of_rows = None):
        """Actually sends the given query to the database and returns the result.
        If query is None, then it uses the most recent query. If number_of_rows is
        None, then it displays all rows in result. By default, Quest does not SHOW
        until the user specifically commands it. The <FILL ME IN> setting may be
        used to change the default to one of three settings:
        * default to SHOWing every row of every command,
        * default to SHOWing N rows of every command (where N is an integer), or
        * default to SHOWing only when the user asks for it (i.e. the default
          anyway)
        """
        if query is None:
            query = self.most_recent_query()
        if number_of_rows is None:
            number_of_rows = quest.config.number_of_rows_to_show

        return self.connection.execute(query)

# Singleton
engine_instance = Engine()
