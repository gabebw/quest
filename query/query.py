# The basic Query class
# TODO: maybe use a tree to track parent/child relationships, since we can have
# 2 children of a query, say if user does ROLLUP(Q, <pred>) and
# ROLLUP(Q, <another_pred>).

import quest.engine
import lexer

from sqlparse import tokens.Token.Keyword as Keyword

class Query:
    def __init__(self, statement, parent = None):
        """statement must be the output of lexer.lex(i_am_a_sql_string).
        parent is the "parent" Query class; as each Query evolves, it
        notes its parent and child. The "top" query has no parent.
        """
        if not isinstance(statement, sqlparse.sql.Statement)
            raise TypeError("statement arg must be a sqlparse.sql.Statement!")
        self.statement = statement
        self.parent = parent
        # self.child is explicitly set by operators
        self.child = None

    def narrow(self, predicate):
        """AND's this query with the given predicate."""
        new_statement = lexer.lex(" ".join(str(self.statement), "AND", predicate))
        # Pass in self as new_query's parent
        new_query = Query(new_statement, self)
        self.child = new_query
        return self.child

    def relax(self, predicate):
        """OR's this query with the given predicate."""
        new_statement = lexer.lex(" ".join(str(self.statement), "OR", predicate))
        # Pass in self as new_query's parent
        new_query = Query(new_statement, self)
        self.child = new_query
        return self.child

    def show(self, number_of_rows = None):
        """Actually sends the query to the DB. If number_of_rows is None (the
        default), then the query gets all results.
        """
        result = quest.engine.show(self.build_query(), number_of_rows)
        return result

    def build_query(self):
        """Compiles self.sql_dict to a SQL string."""
        return str(self.statement)

    def store(self, table_name):
        """Store result of running this query in a table with name
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
            pass
