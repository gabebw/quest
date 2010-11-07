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
ROWS_TO_SHOW = ALL_ROWS
