# Configuration settings for Quest.

# Users can either have Quest show the result of every query, or only show when
# they explicitly ask for it. For each of those 2 cases, they can either specify
# how many rows they want, or leave it blank. These config settings come into
# play in all 4 cases.
# There are 2 main settings:
# ALWAYS_SHOW: True or False; if True then we always show every query, and use
#              SHOW_BEHAVIOR to check how many rows to show
# ROWS_TO_SHOW: Either ALL_ROWS or an integer. If set to ALL_ROWS, we show all rows
# whenever we SHOW. If set to an integer, then we show that many rows.

# This setting controls what happens whenever we SHOW (either at user's request
# or automatically).
# Show all rows of result
ALL_ROWS = "all"

# Default to always showing every query
ALWAYS_SHOW = True
# When we are asked to show a query, and user doesn't specify how many rows to
# show, we show this many rows. Can be either ALL_ROWS or an integer.
ROWS_TO_SHOW = 10


# DB configuration. You should change this in your local config.py, by
# doing:
#  import quest.config
#  quest.config.db_user = "my_db_user"
#  quest.config.db_password = "my_db_password"
#  ...etc.
db_host = 'localhost'
db_user = 'root'
db_password = 'CHANGE_ME'
db_name = 'test'

# ROLLUP/DRILLDOWN hierarchies. Please use the convenience method
# create_hierarchy (below) instead of accessing them directly.
rollup_child2parent = {}
drilldown_parent2child = {}

def create_hierarchy(lst):
    """
    Given a list structure where list[N] is the parent of list[N+1]
    (i.e. parents come before children), populates the hierarchy
    dictionaries for rollup and drilldown. All items in lst are
    strip()ped.

    WARNING: if an attribute of the same name is later added to the
    hierarchies, it will overwrite any previous attribute of the same
    name, so e.g. if we have a relationship where "Mac" rolls up to
    "PC", and later we add a relationship where "Mac" rolls up to
    "Linux", then the "Linux" relationship will overwrite the "PC" one.
    """
    if len(lst) < 2:
        raise Exception("create_hierarchy: list too short (length must be >= 2)")

    global rollup_child2parent
    global drilldown_parent2child
    lst = [elem.strip() for elem in lst]

    for index, item in enumerate(lst):
        if index == 0:
            # First element, can only drill down
            drilldown_parent2child[item] = lst[index+1]
        elif index == len(lst)-1:
            # Last element, can only roll up
            rollup_child2parent[item] = lst[index-1]
        else:
            # Neither first nor last element, add to both hierarchies
            rollup_child2parent[item] = lst[index-1]
            drilldown_parent2child[item] = lst[index+1]
