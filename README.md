# aws-lambda-get-event-detail
Python3 program and lambda event handler that returns various details about the
function execution environment formatted in CSS/HTML

##Function returns the following:

    - Location data based on the IP address of the execution environment
    - Platform Execution information
    - Data passed from the browser client via API Gateway
    - A few attributes of the function execution context

    Since program returns CSS/HTML code vs. the typical json, important that
    Integration Response in API Gateway is configured correctly. Specifically,

##Integration Response

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
