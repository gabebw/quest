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
order to connect to the MySQL database. It reads these values from a config
file called ``quest_config.conf``, which should be in the same directory as
the script that is running quest.

This is a sample ``quest_config.conf``::
  [quest]
  # Every field in [quest] is required
  db_user = root
  db_password = puppies
  # Quest only connects to 1 table
  table_name = employees
  db_name = company

  # These are used by ROLLUP and DRILLDOWN.
  # Parents come before children.
  [hierarchies]
  ceo,manager,employee

Usage
-----
Typical usage of the command-line REPL::
    #!/usr/bin/env python

    import quest
    from quest.prompt import Prompt

    p = Prompt()
    p.interact()

Typical usage of the HTML GUI::
    #!/usr/bin/env python

    import quest
    from quest.web import quest_app
    quest_app.run()
    # Now navigate to http://localhost:8080
