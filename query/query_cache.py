# Stores all queries using simple key-value system, where the value is a Query
# instance. Each key is either user-specified name (e.g. "my_awesome_query")
# or if user doesn't specify a name, then an autogenerated name (e.g. "Q20").
# This is a singleton class implemented using a module (rather than a class).

from string import uppercase

class TooManyQueryVariables(Exception):
    def __init__(self, value):
        self.value = value

# The actual cache dict. query_cache is just a wrapper around this.
cache = {}
# counter_dict tracks the current "generation" of a query variable, e.g.
# if we're in the 3rd generation of Q, then counter_dict["Q"] == 3. Each
# time an operation is applied to a query, that creates a new
# generation, so e.g. Q4 == Q3.rollup(<predicate>)
# Each time INITIALIZE is called, adds a new key with the counter set to
# 0.
counter_dict = {}
uppercase_list = list(uppercase)
# most_recent_query is set whenever put() is called.
most_recent_query = None

def increment_counter_for(variable):
    """Increment the counter for a given variable name."""
    counter_dict[variable] += 1

def next_variable_name(letters = uppercase_list):
    """Searches _cache_ to get the next unused variable name. Checks
    "A"-"Z", then "AA"-"ZZ", etc. and uses first letter that hasn't been
    used yet. The letters argument allows for recursive calling with
    different sets of letters.
    """
    if len(letters[0]) == 4:
        # We've reached "AAAA", stop.
        raise TooManyQueryVariables("Too many query variables!")

    next_variable_name = ""
    cache_keys = cache.keys()
    unused_letters = [letter for letter in letters if letter not in cache_keys]
    if len(unused_letters) == 0:
        # All letters are used, recurse.
        # "A" -> "AA", "AA" -> "AAA", etc.
        new_letters = [letter + letter for letter in letters]
        next_variable_name = next_variable_name(new_letters)
    else:
        # There are unused letters, take the first one
        next_variable_name = unused_letters[0]
    return next_variable_name

def put(key, value):
    """Put a (key, value) pair in the cache. Returns a (key, value) tuple."""
    cache[key] = value
    most_recent_query = value
    return (key, value)

def get(key):
    """Returns the value associated with the given key. Behaves exactly like a
    dict (since that's what it uses) if the key is not in the cache. That is, it
    raises a KeyError.
    """
    return cache[key]

def delete(key):
    """Delete the key from the cache. Raises a KeyError (exactly like a dict)
    if the key is not in the cache. Returns the key.
    """
    del cache[key]
    return key