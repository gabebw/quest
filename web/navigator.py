#!/usr/local/bin/python

import cgi
import cgitb
import os
import urllib

cgitb.enable()

import quest
from quest import config

# Must set before importing anything else!
config.db_name = 'baseball'
config.db_password = 'bergstrom'

from quest.query.handle_user_input import handle_user_input

def http_headers():
    print "Content-Type: text/html\n"

def run():
    try:
        http_headers()
        buttons = cgi.FieldStorage()
        query = buttons.getvalue('query')
    except:
        http_headers()
        print "<hr><h1>Oops! A Quest-related error occurred.</h1>"
        cgi.print_exception()
    else:
        # Handle errors raised by Quest separately
        try:
            print str(handle_user_input(query)).strip()
        except:
            http_headers()
            print "<hr><h1>Oops! Quest couldn't handle your input.</h1>"
            cgi.print_exception()


run()
