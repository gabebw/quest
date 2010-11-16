# The basic Query class
# TODO: maybe use a tree to track parent/child relationships, since we can have
# 2 children of a query, say if user does ROLLUP(Q, <pred>) and
# ROLLUP(Q, <another_pred>).

from collections import OrderedDict

import quest.engine

class Query:
    def __init__(self, sql_dict, parent = None):
        """The sql_dict is an OrderedDict with keys for each part of a SQL query,
        e.g. sql_dict["SELECT"] == "*", sql_dict["FROM"] == "users", etc. parent
        is the "parent" Query class; as each Query evolves, it notes its parent
        and child. The "top" query has no parent.
        """
        if not isinstance(sql_dict, OrderedDict):
            raise TypeError("sql_dict must be an OrderedDict!")
        self.sql_dict = sql_dict
        self.parent = parent
        # self.child is explicitly set by operators
        self.child = None
        self.engine = quest.engine

    def narrow(self, predicate):
        new_sql_dict = sql_dict
        new_sql_dict["WHERE"] += " AND " + predicate
        # Set this query as the new query's parent
        new_query = Query(new_sql_dict, self)
        self.child = new_query
        return self.child

    def relax(self, predicate):
        new_sql_dict = sql_dict
        new_sql_dict["WHERE"] += " OR " + predicate
        # Set this query as the new query's parent
        new_query = Query(new_sql_dict, self)
        self.child = new_query
        return self.child

    def show(self, number_of_rows = None):
        """Actually sends the query to the DB. If number_of_rows is None (the
        default), then the query gets all results.
        """
        # TODO: pass in number of rows to run_sql
        result = self.engine.run_sql(self.build_query(), number_of_rows)
        return result

    def build_query(self):
        """Compiles self.sql_dict to a SQL string."""
        sql = ""
        # Say sql_dict = {"SELECT": "*", "FROM": "users"}
        # then sql = "SELECT * FROM users", since it's ordered.
        for (operator, args) in self.sql_dict.iteritems():
            sql += " " + operator + " " + args
        return sql.strip()

    def get_sql_dict(self):
        return self.sql_dict
