===========
Quest
===========
---------------------------------
Query Engine for Selecting Tables
---------------------------------

Installation
------------
Easy enough::
  easy_install quest
or::
  pip install quest

Intro
-----
Quest implements a simple DSL (domain-specific language) on top of MySQL.
It can connect to any MySQL database. It can be used at the command line,
which provides a simple REPL, or through an HTML GUI.

Configuration
-------------
Quest must have access to a username and password of a MySQL account in
order to connect to the MySQL database. You should set these in your script
by doing (e.g.)::
  import quest.config
  quest.config.db_host = localhost # default
  quest.config.db_user = root # default
  quest.config.db_password = puppies
  # Quest only connects to 1 table
  quest.config.table_name = employees
  quest.config.db_name = company

To create a hierarchy for ROLLUP (which goes up the hierarchy) and DRILLDOWN
(which goes down the hierarchy), use quest.config.create_hierarchy::
  # Parents come before children.
  quest.config.create_hierarchy(['ceo', 'manager', 'employee'])
  quest.config.create_hierarchy(['python', 'cpp', 'c'])

Usage
-----
Typical usage of the command-line REPL::
    #!/usr/bin/env python

    import quest
    import quest.config
    from quest.prompt import Prompt

    quest.config.db_host = localhost # default
    quest.config.db_user = root # default
    quest.config.db_password = puppies
    # Quest only connects to 1 table
    quest.config.table_name = employees
    quest.config.db_name = company

    p = Prompt()
    p.interact()

Typical usage of the HTML GUI::
    #!/usr/bin/env python

    import quest
    import quest.config
    from quest.web import quest_app

    quest.config.db_host = localhost # default
    quest.config.db_user = root # default
    quest.config.db_password = puppies
    # Quest only connects to 1 table
    quest.config.table_name = employees
    quest.config.db_name = company

    quest_app.run()
    # Now navigate to http://localhost:8080
