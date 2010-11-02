# Configuration settings for Quest.

# Only show results when user explicitly asks for them
SHOW_NONE = 'show_none'
# Always show first N results, where N == number_of_rows_to_show
SHOW_N = 'show_n'
# Always show all rows of every result
SHOW_ALL = 'show_all'

# When show_behavior == SHOW_N, this variable is used to determine how many rows
# to show.
number_of_rows_to_show = 20

# Default to always showing all rows
show_behavior = SHOW_ALL
