from sqlalchemy.sql import select

# Splits "SELECT title, count(*) AS authors FROM Book NATURAL JOIN Book_author GROUP BY title;"
# into ['', 'SELECT', 'title, count', 'AS', 'authors', 'FROM', 'Book',
# 'NATURAL JOIN', 'Book_author', 'GROUP BY', 'title;']
regexp_sql = re.compile(r'\W*([A-Z]+)\W+')

def compile_to_sqlalchemy(sql):
    sql = sql.strip()
    split_array = re.split(regexp_sql, sql)
    # Remove blank strings
    split_array=  [x for x in split_array if x != '']
    sql_dict = {}
    for i in range(0, len(split_array), 2):
        # e.g. "SELECT"
        sql_operator = split_array[i:i+1][0].upper()
        # e.g. ["*"]
        operator_args = re.split(r'\W*,\W*', split_array[i+1:i+2][0])
        sql_dict[sql_operator] = operator_args

    if 'SELECT' not in sql_dict:
        raise "compile_to_sqlalchemy currently only deals with SELECTs"

    query = select(sql_dict['SELECT'])
