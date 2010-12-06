#!/usr/local/bin/python

import cgi
import cgitb
import os
import urllib

cgitb.enable()

def run():
    try:
        http_headers()
        print '''
                <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
                <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                <title>Quest</title>
                <style type="text/css">
                    #query {
                        width: 800px;
                        height: 45px;
                    }
                </style>

                <script type="text/javascript" src="jquery-1.4.4.min.js"></script>
                <script type="text/javascript">
                    $(document).ready(function(){
                        $('#theForm').submit(function(e){
                            e.preventDefault();
                            $.get('navigator.py',
                                {query: $('#query').val()},
                                function(data, textStatus, xhr){
                                    $('#mySearch').html(data);
                                });
                        });
                    });
                </script>
                </head>
                <body>

                <table>
                    <h1 align="center">QUEST</h1>
                    <tr>
                        <form id="theForm">
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
         '''.strip()
    except:
        http_headers()
        print "<h1>Oops...an error occurred.</h1>"
        cgi.print_exception()

def http_headers():
    """Prints out the headers so we can show something on the screen."""
    print "Content-Type: text/html\n"

run()
