from json import loads
import platform
import logging
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

    S3_BASE = '< Location of S3 bucket used to hold CSS and Favicon files >'

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

    # This is the main part of the routine and forms the HTML Body section and
    # needs to be constructed of pure HTML as we will be returning only HTML to
    # a browser client

    html_body = "<body>"
    html_body += "<h1>AWS Lambda Function Event Details</h1>"

    html_body += "<div align = center>"
    html_body +=  "<button class='button' onclick='location.reload();'>"
    html_body +=   "Refresh Page"
    html_body += "</button></div>"

    html_body += "<section class='container'>"

    # Location detail based on IP address of calling function

    my_geo = get_IP_geo()
    html_body += "<h2>Location Detail based on IP lookup</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"
    for k, v in my_geo.items():
        html_body += "<li><strong>{}</strong>: {}</li>".format(k, v)
    html_body += "</ul>"
    html_body += "</div>"

    # Platform Execution Environment details

    html_body += "<h2>Platform Execution Detail</h2>"
    html_body += "<div class='detail'>"
    html_body += "<ul>"
    for k, v in platform_data.items():
        html_body += "<li><strong>{}</strong>: {}</li>".format(k, v)
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
                    html_body += "<li><strong>{}</strong>: {}</li>".format(k2, v2)
            else:
                html_body += "<li><strong>{}</strong>: {}</li>".format(k1, v1)
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
    html_body += "<li>Time used (MS): {}</li>".format(
                  3000 - context.get_remaining_time_in_millis())
    html_body += "<li>Time budget remaining (MS): {}</li>".format(
                  context.get_remaining_time_in_millis())
    html_body += "<li>Memory limits (MB): {}</li>".format(
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
