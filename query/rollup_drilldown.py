import sqlparse
from quest import QuestOperationNotAllowedException

# User-provided hierarchies.
from config import drilldown_parent2child, rollup_child2parent

def drilldown(query, parent_attribute):
    """
    Takes a query and parent attribute to drilldown on -- i.e. return
    a query with the parent attribute's child instead of the parent attribute.
    """
    if parent not in drilldown_parent2child:
        error_message = "Cannot DRILLDOWN on %s. Can DRILLDOWN on any of these: %s" % (parent_attribute, ", ".join(drilldown_parent2child.keys()))
        raise QuestOperationNotAllowedException(error_message)

    child_attribute = drilldown_parent2child[parent_attribute]
    return replace_and_create_new_query(query, parent_attribute, child_attribute)

def rollup(query, child_attribute):
    """
    Takes a query and child attribute to rollup on -- i.e. return a
    a query with the child attribute's parent instead of the child attribute.
    """
    if child_attribute not in rollup_child2parent:
        error_message = "Cannot ROLLUP on %s. Can ROLLUP on any of these: %s" % (child_attribute, ", ".join(rollup_child2parent.keys()))
        raise QuestOperationNotAllowedException(error_message)

    parent_attribute = rollup_child2parent[child_attribute]
    return replace_and_create_new_query(query, child_attribute, parent_attribute)

def replace_and_create_new_query(query, target_attribute, new_attribute):
    """
    Replace target_attribute with new_attribute in query and return new
    query string.
    """
    parsed = sqlparse.parse(query)
    new_query = ""
    for statement in parsed:
        replace_text = False
        for token in statement.tokens:
            if str(token).lower() in ['select', 'by']:
                replace_text = True
                next

            if replace_text and not token.is_whitespace():
                # Replace the first non-whitespace token after "SELECT"
                # or "BY"
                token = replace_attribute(str(token), target_attribute, new_attribute)
                replace_text = False

            new_query.append(str(token).strip())
    return " ".join([token for token in new_query if token != ''])

def replace_attribute(attributes, target_attribute, new_attribute):
    """
    A helper function for drilldown and rollup. Given all
    attributes, replaces targetAttribute with newAttribute and returns
    the result.
    """
    split_attributes = attributes.split(",")

    # Replace all occurrences of target_attribute with new_attribute and
    # leave other attributes alone.
    replaced_attributes = [new_attribute if elem == target_attribute else elem for elem in split_attributes]
    # Strip everything.
    replaced_attributes = [att.strip() for att in replaced_attributes]
    return ", ".join(replaced_attributes)
