from json import loads
import platform
import logging
import subprocess
from urllib.request import urlopen

''' Python 3 Lambda function that returns the following in raw HTML/CSS:

    - Location data based on the IP address of the function execution environment

    - Data passed from the browser client via API Gateway

    - Various attributes of the function execution context
'''

# For info on provisioning API gateway, please see README.md @
# https://github.com/mikeoc61/aws-lambda-get-event-detail

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

platform_data = {
    'system': platform.system(),
    'platform': platform.platform(),
    'nodename': platform.node(),
    'machine': platform.machine(),
    'architecture': platform.architecture(),
    'processor': platform.processor(),
    'python': platform.python_version()
    }


# OS Commands to execute. Key will be displayed and Value will be executed.
# Note command to be executed must be provided as an array of strings

os_commands = {
    'ps -ef': ['ps', '-ef'],
    'ls -lA': ['ls', '-lA'],
    'uptime': ['uptime']
}

def get_IP_geo():
    '''Get location related data from web service: http://ipinfo.io/json'''

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
        logger.error("Error opening: %s, using default location", geo_URL)
    else:
        if (webUrl.getcode() == 200):
            geo_data = webUrl.read()
            geo_json = loads(geo_data.decode('utf-8'))
            geo_json['loc'] = geo_json['loc'].split(',')
        else:
            logger.error("webUrl.getcode() returned: %s", webUrl.getcode())
            logger.error("Using default location data")

    return geo_json

def build_response(event, context):
    '''Using event and context data structures provided by the event
       handler, build a DOM formatted as CSS/HTML/Javascript consisting
       of information about the execution environment and return DOM
       to the lambda event handler.
    '''

    # Link to supporting CSS Stylesheet and Favicon stored on S3

    S3_BASE = 'https://www.mikeoc.me/projects/lambda_event_detail/'

    CSS_FILE = S3_BASE + 'styles.css'
    CSS_LINK = "rel='stylesheet' type='text/css' href='{}'".format(CSS_FILE)

    ICO_FILE = S3_BASE + 'favicon.ico'
    ICO_LINK = "rel='icon' type='image/x-icon' href='{}'".format(ICO_FILE)

    logger.info("CSS_FILE = %s", CSS_FILE)
    logger.info("ICO_FILE = %s", ICO_FILE)

    html_head = "<!DOCTYPE html>"
    html_head +=  "<head lang='en'>"
    html_head +=  "<title>Display Lambda Function Detail</title>"
    html_head +=  "<link " + CSS_LINK + ">"
    html_head +=  "<link " + ICO_LINK + ">"
    html_head += "</head>"

    # This is the main part of the routine and forms the HTML Body
    # section of the DOM we will build and return to client.

    VAL_COL = "<span style='color:#3ad900;'>"   # Limegreen text

    html_body = "<body>"
    html_body += "<h1>AWS Lambda Function Event Details</h1>"

    html_body += "<div align = center>"
    html_body +=  "<button class='button' onclick='location.reload();'>"
    html_body +=   "Refresh Page"
    html_body += "</button></div>"

    html_body += "<section class='container'>"

    # Location detail based on IP address of calling function

    my_geo = get_IP_geo()
    html_body += "<h2>Container location based on IP lookup</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"
    for k, v in my_geo.items():
        html_body += "<li>" + k.capitalize() + ": " + VAL_COL + str(v) + "</li>"
    html_body += "</ul>"
    html_body += "</div>"

    # Platform Execution Environment details

    html_body += "<h2>Platform Execution Detail</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"
    for k, v in platform_data.items():
        html_body += "<li>" + k.capitalize() + ": " + VAL_COL + str(v) + "</li>"
    html_body += "</ul>"
    html_body += "</div>"

    # OS Command Execution output

    html_body += "<h2>OS Command Execution Output</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"

    # For each OS command in data structure, execute and display output
    for k, v in os_commands.items():
        p = subprocess.Popen(v, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            html_body += "<li>" + k + ": " + VAL_COL + line.decode('utf-8').strip(' ') + "</li>"

    html_body += "</ul>"
    html_body += "</div>"

    # Event detail based on format defined by API gateway Integration Request
    # mapping template for method invoked. Loop through data structures in
    # the event{} object and convert to HTML list items.

    html_body += "<h2>Client Request Detail</h2>"

    html_body += "<div class='detail'>"
    html_body += "<ul>"
    for k, v in event.items():
        html_body += "<h3>{}</h3>".format(k.upper())
        logger.info("Key %s = %s", k, v)
        for k1, v1 in v.items():
            if isinstance (v1, dict):
                html_body += "<h4>{}</h4>".format(k1.upper())
                for k2, v2 in v1.items():
                    html_body += "<li>" + k2.capitalize() + ": " + VAL_COL + str(v2) + "</li>"
            else:
                html_body += "<li>" + k1.capitalize() + ": " + VAL_COL + str(v1) + "</li>"
    html_body += "</ul>"
    html_body += "</div>"

    # Display some context attributes for this lambda function. See:
    # https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    html_body += "<h2>Event Context Detail</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"
    html_body += "<li>Function name: " + VAL_COL +  "{}</li>".format(context.function_name)
    html_body += "<li>Function version: " + VAL_COL + "{}</li>".format(context.function_version)
    html_body += "<li>Function ARN: " + VAL_COL +  "{}</li>".format(context.invoked_function_arn)
    html_body += "<li>Request ID: " + VAL_COL + "{}</li>".format(context.aws_request_id)
    html_body += "<br>"
    html_body += "<li>Time used (MS): " + VAL_COL + "{}</li>".format(
                  3000 - context.get_remaining_time_in_millis())
    html_body += "<li>Time budget remaining (MS): " + VAL_COL +  "{}</li>".format(
                  context.get_remaining_time_in_millis())
    html_body += "<li>Memory limits (MB): " + VAL_COL +  "{}</li>".format(
                  context.memory_limit_in_mb)
    html_body += "</ul>"
    html_body += "</div>"

    # Finished with HTML formatting

    html_body += "</section>"
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

    logger.info('Event: %s', event)
    logger.info('Context: %s', context)

    return build_response(event, context)
