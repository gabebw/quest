"""
The actual engine that ties the whole backend together. Delegates a lot of stuff
to quest.*.
"""

from sqlalchemy.sql.expression import text

import quest.operators

class Engine:
    def __init__(self):
        self.queries = []

    def most_recent_query(self):
        """Return the most recent query, or None if empty.."""
        try:
            return self.queries[-1]
        except IndexError:
            return None

    def apply_operator(self, operator_name, query, predicate):
        """Apply the given operator_name to the query using the given predicate.

        Appends the result to self.queries and returns the new query. 
        operator_name should exist in quest.operators. If it doesn't, then
        prints an AttributeError and returns False.
        For more on what each operator does, see operators/<operator_name>.py.
        """

        operator_name = operator_name.lower()

        # Get the function, e.g. quest.operators.drilldown
        try:
            operator = getattr(quest.operators, operator_name)
        except AttributeError as ae:
            print ae
            return False
        else:
            new_query = operator(query, predicate)
            self.queries.append(new_query)
            return new_query

    def run_sql(self, sql):
        """Evaluates a pure SQL expression. Currently just prints it."""
        t = text(answer)
        print t
        # TODO: should this be translated to SQLAlchemy first?
        self.queries.append(t)
        return t
        #return connection.execute(t)

#    def rollup(self, query, predicate):
#        """Apply the rollup operator to the query using the given predicate.
#
#        Appends the result of applying the operator to self.queries and returns
#        the new query.
#        """
#        new_query = quest.operators.rollup(query, predicate)
#        self.queries.append(new_query)
#        return new_query
#
#    def drilldown(self, query, predicate):
#        """Apply the drilldown operator to the query using the given predicate.
#
#        Appends the result of applying the operator to self.queries and returns
#        the new query.
#        """
#        new_query = quest.operators.drilldown(query, predicate)
#        self.queries.append(new_query)
#        return new_query
#
#    def store(self, query, predicate):
#        """Apply the store operator to the query using the given predicate.
#
#        Appends the result of applying the operator to self.queries and returns
#        the new query.
#        """
#        new_query = quest.operators.store(query, predicate)
#        self.queries.append(new_query)
#        return new_query
#
#    def relate(self, query, predicate):
#        """Apply the relate operator to the query using the given predicate.
#
#        Appends the result of applying the operator to self.queries and returns
#        the new query.
#        """
#        new_query = quest.operators.relate(query, predicate)
#        self.queries.append(new_query)
#        return new_query
#
#    def relax(self, query, predicate):
#        """Apply the relax operator to the query using the given predicate.
#
#        Appends the result of applying the operator to self.queries and returns
#        the new query.
#        """
#        new_query = quest.operators.relax(query, predicate)
#        self.queries.append(new_query)
#        return new_query
#
#    def narrow(self, query, predicate):
#        """Apply the narrow operator to the query using the given predicate.
#
#        Appends the result of applying the operator to self.queries and returns
#        the new query.
#        """
#        new_query = quest.operators.narrow(query, predicate)
#        self.queries.append(new_query)
#        return new_query
