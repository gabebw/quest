# The basic Query class

import re

import quest.engine
# for RSHIFT/LSHIFT
import shifter
import rollup_drilldown

class Query:
    rBeginsWithSelect = re.compile("^select", re.I)

    def __init__(self, query_string, parent = None):
        """
        query_string is the string representation of the query.
        parent is the "parent" Query class; as each Query evolves, it
        notes its parent and child. The "top" query has no parent.
        """
        self.statement = query_string.strip()
        self.parent = parent
        # self.child is explicitly set by operators
        self.child = None

    def narrow(self, clause):
        """AND's this query with the given predicate."""
        query = self.statement.split()
        i=0

        hasWhereOrHaving=False
        hasFrom=False

        while i<len(query):
            token = query[i]
            lower_token = token.lower()
            if lower_token == "from":
                hasFrom=True

            elif lower_token in ["where", "having"] and hasFrom:
                hasWhereOrHaving=True
                query[i] = " ".join([token, clause, "and"])
            i+=1

        if hasFrom and not hasWhereOrHaving:
            query.append("where "+clause)

        return self.set_child_and_return(' '.join(query))

    def relax(self, clause):
        """OR's this query with the given predicate."""
        query = self.statement.split()
        i=0

        hasWhereOrHaving=False
        hasFrom=False

        while i<len(query):
            token = query[i]
            lower_token = token.lower()
            if lower_token == "from":
                hasFrom=True

            elif lower_token in ["where", "having"] and hasFrom:
                hasWhereOrHaving=True
                query[i] = " ".join([token, clause, "or"])
            i+=1

        if hasFrom and not hasWhereOrHaving:
            query.append("where "+clause)

        return self.set_child_and_return(' '.join(query))

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
        successfully stored, raises the error it encountered with some
        extra Quest-specific info prepended to the error message.
        """
        match = self.rBeginsWithSelect.match(self.statement)
        if match:
            # This is a SELECT statement, proceed
            # CREATE TABLE new_table_name SELECT ...
            query = "CREATE TABLE %s %s" % (table_name, self.statement)
            try:
                quest.engine.run_sql(query)
                # Don't set child, because this is just saving to a
                # variable
                return query
            except Exception, e:
                # Prepend some of our own info onto the exception
                raise e.__class__("Could not store: %s" % repr(e))
        else:
            # Not a SELECT, ????
            raise TypeError("Query is not a SELECT, what's going on?: %s" % self)

    def relate(self, other_query):
        """
        Return a string representation of a natural inner join query
        between this query and other_query.
        """
        statement_without_semicolon = self.statement
        if self.statement.endswith(";"):
            statement_without_semicolon = self.statement[:-1].strip()
        return self.set_child_and_return("SELECT * FROM %s NATURAL INNER JOIN %s" % (statement_without_semicolon, other_query))

    def lshift(self, attr):
        """LSHIFT an attribute of this query."""
        return self.set_child_and_return(shifter.lshift(self.statement, attr))

    def rshift(self, attr):
        """RSHIFT an attribute of this query."""
        return self.set_child_and_return(shifter.rshift(self.statement, attr))

    def rollup(self, attr):
        return self.set_child_and_return(rollup_drilldown.rollup(self.statement, attr))

    def drilldown(self, attr):
        return self.set_child_and_return(rollup_drilldown.drilldown(self.statement, attr))

    def set_child_and_return(self, new_statement):
        """Set new_query as self.child and return new_query."""
        # Pass in self as new_query's parent
        new_query = Query(new_statement, self)
        self.child = new_query
        return self.child

    def __str__(self):
        return str(self.statement)
