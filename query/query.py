# The basic Query class
# TODO: maybe use a tree to track parent/child relationships, since we can have
# 2 children of a query, say if user does ROLLUP(Q, <pred>) and
# ROLLUP(Q, <another_pred>).

import quest.engine
# for RSHIFT/LSHIFT
import shifter
import rollup_drilldown

class Query:
    def __init__(self, query_string, parent = None):
        """
        query_string is the string representation of the query.
        parent is the "parent" Query class; as each Query evolves, it
        notes its parent and child. The "top" query has no parent.
        """
        self.statement = statement
        self.parent = parent
        # self.child is explicitly set by operators
        self.child = None

    def narrow(self, predicate):
        """AND's this query with the given predicate."""
        new_statement = lexer.lex(" ".join(str(self.statement), "AND", predicate))
        return set_child_and_return(new_statement)

    def relax(self, predicate):
        """OR's this query with the given predicate."""
        new_statement = lexer.lex(" ".join(str(self.statement), "OR", predicate))
        return set_child_and_return(new_statement)

    def show(self, number_of_rows = None):
        """
        Actually sends the query to the DB. If number_of_rows is None (the
        default), then the query gets all results.
        """
        result = quest.engine.show(self.statement, number_of_rows)
        return result

    def store(self, table_name):
        """
        Store result of running this query in a table with name
        table_name. Returns True if successfully stored. If it wasn't
        successfully stored, prints the error it encountered and returns
        False.
        """
        if self.statement.tokens[0].ttype == Keyword.DML:
            # CREATE TABLE AS <select>
            # This is a SELECT statement, proceed
            query = "CREATE TABLE {} AS {}".format(table_name, self.statement)
            try:
                quest.engine.run_sql(query)
                return True
            except Exception as e:
                print "Could not store: " + e
                return False
        else:
            # Not a SELECT, ????
            raise TypeError("Query is not a SELECT, what's going on?: %s" % self)

    def relate(self, other_query):
        """
        Return a string representation of a natural inner join query
        between this query and other_query.
        """
        return "SELECT * FROM %s NATURAL INNER JOIN %s" % (self, other_query)

    def lshift(self, attr):
        """LSHIFT an attribute of this query."""
        return set_child_and_return(shifter.lshift(self, attr))

    def rshift(self, attr):
        """RSHIFT an attribute of this query."""
        return set_child_and_return(shifter.rshift(self, attr))

    def rollup(self, attr):
        return set_child_and_return(rollup_drilldown.rollup(self.statement, attr))

    def drilldown(self, attr):
        return set_child_and_return(rollup_drilldown.drilldown(self.statement, attr))

    def set_child_and_return(self, new_statement):
        """Set new_query as self.child and return new_query."""
        # Pass in self as new_query's parent
        new_query = Query(new_statement, self)
        self.child = new_query
        return self.child
