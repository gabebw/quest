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
                #navbar ul {
                    margin: 0;
                    padding: 5px;
                    list-style-type: none;
                    text-align: center;
                    background-color: #000;
                }

                #navbar ul li { display: inline; }

                #navbar ul li a {
                    text-decoration: none;
                    padding: .2em 1em;
                    color: #fff;
                    background-color: #000;
                }

                #navbar ul li a:hover {
                    color: #000;
                    background-color: #fff;
                }
                </style>

                <script type="text/javascript" src="jquery-1.4.4..min.js"></script>
                <script type="text/javascript">
                    $(document).ready(function(){
                        $('#theForm').submit(function(e){
                            e.preventDefault();
                            $.get('navigator.py',
                                {query: $('#Search').val()},
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
                            Enter your Query <input style="WIDTH: 800px; HEIGHT: 45px" size=48 id="Search" />
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
