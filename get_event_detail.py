from json import loads
import platform
from urllib.request import urlopen

''' Lambda function written in Python 3 that returns returns the following
    in raw HTML:

    - Location data based on the IP address of the function execution environment

    - Data passed from the browser client

    - Various attributes of the function execution context

    For info on provisioning API gateway, please see README.md @
    https://github.com/mikeoc61/aws-lambda-get-event-detail
    '''

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
    except:
        print("Error opening: {}, using default location".format(geo_URL))
    else:
        if (webUrl.getcode() == 200):
            geo_data = webUrl.read()
            geo_json = loads(geo_data.decode('utf-8'))
            geo_json['loc'] = geo_json['loc'].split(',')
        else:
            print("webUrl.getcode() returned: {}".format(webUrl.getcode()))
            print("Using default location data")

    return geo_json

def build_response(event, context):
    '''Using event and context data structures provided by the event
       handler, build a list formatted as CSS/HTML/Javascript consisting
       of information about the execution environment and return list
       to the lambda event handler.
    '''

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

    html_head += ".button {color: black; background-color: #93B874;}"
    html_head += ".button {text-align: center; padding: 5px 20px;}"
    html_head += ".button {border-radius: 4px; cursor: pointer;}"
    html_head += ".button {margin: 4px 2px; font-size: 18px;}"
    html_head += ".button {border: 2px solid green;}"
    html_head += ".button {display: inline-block; text-decoration: none;}"

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

    html_body += "<div align = center>"
    html_body += "<button class='button' onclick='location.reload();'>"
    html_body += "Refresh Page"
    html_body += "</button></div>"

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
    # mapping template for method invoked. Loop through data structures in
    # the event{} object and convert to HTML list items.

    html_body += "<h2>Client Request Detail</h2>"

    html_body += "<div class='detail'>"
    html_body += "<ul>"
    for key, v in event.items():
        html_body += "<h3>{}</h3>".format(key)
        print("{} = {}".format(key, event[key]))
        if isinstance(event[key], dict):
            for attr, val in v.items():
                html_body += "<li>{} = {}</li>".format(attr, v[attr])
        elif isinstance(event[key], str):
            html_body += "<li>{} = {}</li>".format(key, event[key])
    html_body += "</ul>"
    html_body += "</div>"

    # Display some context attributes for this lambda function. See:
    # https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    html_body += "<h2>Event Context Detail</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"
    html_body += "<li>Function name: {}</li>".format(context.function_name)
    html_body += "<li>Function version: {}</li>".format(context.function_version)
    html_body += "<li>Function ARN: {}</li>".format(context.invoked_function_arn)
    html_body += "<li>Request ID: {}</li>".format(context.aws_request_id)
    html_body += "<br>"
    html_body += "<li>Time budget remaining (MS): {}</li>".format(
                  context.get_remaining_time_in_millis())
    html_body += "<li>Memory limits (MB): {}</li>".format(
                  context.memory_limit_in_mb)
    html_body += "</ul>"
    html_body += "</div>"

    # Finished with HTML formatting

    html_body += "</body>"
    html_tail = "</html>"

    # Assemble HTML response and return via API Gateway

    resp = html_head + html_body + html_tail

    return resp

def lambda_handler(event, context):
    '''Main event handler function invoked by API gateway. In this case,
       function simply calls the response_builder function and
       will returns CSS/HTML via the gataway to the client
    '''
    print("In lambda handler")

    return build_response(event, context)
