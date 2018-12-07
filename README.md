# aws-lambda-get-event-detail
Python3 program and lambda event handler that returns various details about the
function execution environment formatted in CSS/HTML

## Function returns the following:
    - Location data based on the IP address of the execution environment
    - Platform Execution information
    - Data passed from the browser client via API Gateway
    - A few attributes of the function execution context

## API Gateway Integration Response
Since program returns CSS/HTML code vs. the typical json, we need to
reconfigure the Integration Response. Here are the console instructions:

  1. In API Gateway, select the API you specified when creating the lamdba function
  2. Select the GET Method for your new lambda function and select Method Response
  3. Expand 200 Response and the click on Add Header under Response Headers for 200
  4. Enter "Content-Type" in the box and click on the check icon to the right
  5. Select the GET Method again from your lambda function on the left side
  6. Select Integration Response and expand 200 to add a new mapping to the
     Content-Type Response Header.
  7. Select the pencil icon to the right and set the Mapping value to:   
     'text/html' (be sure to use single quotes). Save you edit.
  8. Expand the Mapping Template section and delete the "application/json" content type
  9. Select "Add mapping template" and enter "text/html" (without quotes).
  10. Select the "text/html" Content Type and set the template value to:

    #set($inputRoot = $input.path('$'))
    $inputRoot
