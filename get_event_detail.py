#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import platform
from urllib.request import urlopen

''' Lambda function that returns the following in CSS/HTML:

    - Location data based on the IP address of the execution environment
    - Platform Execution information
    - Data passed from the browser client via API Gateway
    - A few attributes of the function execution context

    Since program returns CSS/HTML code vs. the typical json, important that
    Integration Response in API Gateway is configured correctly. Specifically,

    Integration Response

    1. Navigate to the Integration Response for the API's GET method.
    2. Open the 200 Response, Header Mappings, and Mapping Templates.
    3. Edit the Response Header Content-Type and set the Mapping value
        to 'text/html' (be sure to use single quotes). Save
    4. Delete the application/json Content-Type under Mapping Templates.
    5. Add the Content-Type: text/html (without quotes).
    6. Select Mapping Template in the right-hand drop-down box.
    7. Set the value of Template to:

        #set($inputRoot = $input.path('$'))
        $inputRoot
 
    Public domain by Michael OConnor <gmikeoc@gmail.com>
    Also available under the terms of MIT license
    Copyright (c) 2018 Michael E. O'Connor
    '''

__version__ = "1.2"


platform_data = {
    'system': platform.system(),
    'platform': platform.platform(),
    'nodename': platform.node(),
    'machine': platform.machine(),
    'architecture': platform.architecture(),
    'processor': platform.processor(),
    'python': platform.python_version()
    }

def get_IP_geo():
    '''Get location related data from seb service: http://ipinfo.io/json'''

    geo_URL = "http://ipinfo.io/json"

    # Initialize data structure we will use to build and return to caller so
    # that function will still return data in and expected format if call fails

    geo_json = {
    "ip": "123.123.123.123",
    "city": "AnyTown",
    "region": "AnyState",
    "country": "AnyCountry",
    "loc": ["99.9999", "-99.9999"],
    "postal": "90210",
    "org": "MickeyMouse Technologies Inc."
    }

    # Open the URL and read the data, if successful decode bytestring and
    # split lat and long into separate strings for easier handling

    try:
        webUrl = urlopen (geo_URL)
        if (webUrl.getcode() == 200):
            geo_data = webUrl.read()
            geo_json = json.loads(geo_data.decode('utf-8'))
            geo_json['loc'] = geo_json['loc'].split(',')
        else:
            print ("Geo service unavailable, using default location")
    except:
        print ("Error opening: {}, using default location".format(geo_URL))

    return geo_json


def lambda_handler(event, context):
    '''Main event handler function invoked by API gateway. In this case,
       function will return onl raw HTML via the gataway to the client
    '''
    print("In lambda handler")

    # Format the Head section of the DOM including any CSS formatting to
    # apply to the remainder of the document. Break into multiple lines for
    # improved readability

    html_head = "<!DOCTYPE html>"
    html_head += "<head>"
    html_head += "<title>Display Lambda Function Detail</title>"
    html_head += "<style>"
    html_head += "body {background-color: #93B874;}"
    html_head += ".detail {position: relative; left: 30px;}"
    html_head += ".detail {border: 3px solid green;}"
    html_head += ".detail {border-radius: 5px; padding: 2px;}"
    html_head += ".detail {width: 620px;}"
    html_head += ".detail {margin-left: 20px;}"
    html_head += "ul {list-style-position: inside; word-break: break-all;}"
    html_head += "ul {padding-left: 20px; margin-left: 20px; text-indent: -20px}"
    html_head += "ul {font-family: 'Times New Roman', Times, serif;}"
    html_head += "ul {font-size: 14px;}"
    html_head += "h1 {text-align: center;}"
    html_head += "h2 {margin-left: 10px;}"
    html_head += "h3 {margin-left: -10px;}"
    html_head += "</style>"
    html_head += "</head>"

    # This is the main part of the routine and forms the HTML Body section and
    # needs to be constructed of pure HTML as we will be returning only HTML to
    # a browser client

    html_body = "<body>"
    html_body += "<h1>AWS Lambda Function Event Details</h1>"
    #html_body += "<div class='box'>Float</div>"
    #html_body += ".box {float: left; width: 150px; height: 150px; margin-right: 30px;}"

    # Location detail based on IP address of calling function

    my_geo = get_IP_geo()
    html_body += "<h2>Location Detail based on IP lookup</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"
    for k, v in my_geo.items():
        html_body += "<li>{} = {}</li>".format(k, v)
    html_body += "</ul>"
    html_body += "</div>"

    # Platform Execution Environment details

    html_body += "<h2>Platform Execution Detail</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"
    for k, v in platform_data.items():
        html_body += "<li>{} = {}</li>".format(k, v)
    html_body += "</ul>"
    html_body += "</div>"

    # Event detail based on format defined by API gateway Integration Request
    # mapping template for method invoked

    html_body += "<h2>Calling Event Detail</h2>"

    html_body += "<div class='detail'>"
    html_body += "<ul>"
    for key, v in event.items():
        html_body += "<h3>{}</h3>".format(key)
        print("{} = {}".format(key, event[key]))
        if isinstance(event[key], dict):
            #html_body += "<div class='detail'>"
            for attr, val in v.items():
                html_body += "<li>{} = {}</li>".format(attr, v[attr])
    html_body += "</ul>"
    html_body += "</div>"


    # Display some context attributes for this lambda function
    # See: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    html_body += "<h2>Context Stats</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"
    html_body += "<li>Function name: {}</li>".format(context.function_name)
    html_body += "<li>Time remaining(MS): {}</li>".format(
                  context.get_remaining_time_in_millis())
    html_body += "<li>Memory limits(MB): {}</li>".format(
                  context.memory_limit_in_mb)
    html_body += "</ul>"
    html_body += "</div>"

    html_body += "</body>"

    # Closing HTML formatting

    html_tail = "</html>"

    # Assemble HTML response and return via API Gateway

    resp = html_head + html_body + html_tail

    return resp
