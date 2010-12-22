#!/usr/bin/env python

# A simple server to run a local HTML interface to Quest

import os.path
from os.path import dirname
import sys

import cherrypy

import quest
from quest import config
from quest import input_handler

# Used in conf file to serve static assets
current_dir = dirname(os.path.abspath(__file__))
quest_config = os.path.join(dirname(__file__), 'quest_app.conf')

quest_html = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Quest</title>
<style type="text/css">
    #query {
        width: 800px;
        height: 45px;
    }
    /* The div containing the REPL input and result */
    .repl-item {
        border-bottom: 2px solid black;
    }
    /* The user's input, printed back to them */
    .repl-input {
    }
    /* The result of processing a user's query */
    .repl-result {
    }
</style>

<script type="text/javascript" src="/jquery-1.4.4.min.js"></script>
<script type="text/javascript">
    $.ajaxSetup({
        url: "navigate",
        type: "GET"
    });
    $(document).ready(function(){
        $('#theForm').submit(function(e){
            e.preventDefault();
            var userInput = $('#query').val();
            // third param is errorThrown for error callback
            function onSuccessOrError(data, textStatus, xhr){
                var replItem = $("<div/>", {
                    "class": "repl-item",
                    text: userInput});
                replItem.prependTo("#mySearch");

                $("<div/>", {
                    "class": "repl-result"
                // append so the returned value is after
                // the user input value
                }).html(data).appendTo(replItem);
            }
            $.ajax({
                data: {query: userInput},
                success: onSuccessOrError,
                error: onSuccessOrError
            });
        });
    });
</script>
</head>
<body>

<table>
    <h1 align="center">QUEST</h1>
    <tr>
        <form action="navigate" id="theForm">
        <br/>
        <p align="center">
            Enter your Query
            <input id="query" name="query" size=48 />
            <input id="submit" type="submit" value="Submit" />
        </p>
        </form>
    </tr>

    <tr id="mySearch">
        <hr></hr>
    </tr>
</table>
</body>
</html>
""".strip()

class WelcomePage:
    @cherrypy.expose
    def index(self):
        # Ask for the query
        return quest_html

    @cherrypy.expose
    def navigate(self, query = None):
        # CherryPy passes all GET and POST variables as method parameters.
        # It doesn't make a difference where the variables come from, how
        # large their contents are, and so on.
        #
        # You can define default parameter values as usual. In this
        # example, the "name" parameter defaults to None so we can check
        # if a name was actually specified.

        if query:
            try:
                response = str(input_handler.handle(query)).strip()
                # Add a period and <br> instead of newlines
                return response.replace("\n", ".<br/>")
            except Exception:
                return "<hr><h1>Oops! Quest couldn't handle your input.</h1>"
        else:
            if query is None:
                # No name was specified
                return 'Please enter a query.'
            else:
                return 'No, really, enter a query.'


def run():
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.quickstart(WelcomePage(), config=quest_config)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("Usage: %s db_name db_password" % __file__)
    else:
        config.db_name = sys.argv[1]
        config.db_password = sys.argv[2]
        cherrypy.quickstart(WelcomePage(), config=quest_config)
