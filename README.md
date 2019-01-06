# aws-lambda-get-event-detail
Python3 program and lambda event handler that returns various details about the
function execution environment formatted in CSS/HTML

## Function returns the following:
    - Location data based on the IP address of the execution environment
    - Platform Execution information
    - Data passed from the browser client via API Gateway
    - A few attributes of the function execution context

You can test the function by visiting: [https://api.mikeoc.me/service/beta/showEventDetail] (https://api.mikeoc.me/service/beta/showEventDetail?key1=value2&key2=value2)

## API Gateway Method Execution
Since program returns CSS/HTML code vs. the typical json, we need to
reconfigure the API Gateway Integration Response associated with the Method Execution. To define a custom response mapping we'll also have to disable Integration Request default Proxy behavior and optionally create a new Request Mapping template. Both
the provided mapping template and the one listed below work with this code.
Also remember to Deploy the API following any changes to
Method Execution. Here are the relevant console instructions:

### For Integration Request
1. In API Gateway, select the API you specified when creating the lamdba function
2. Select the GET Method for your new lambda function and select Integration Request
3. To add a custom integration template, uncheck the box next to
   Use Lambda Proxy integration and add the new template under Mapping Templates
4. Add Content-Type 'application/json' (don't include quotes)
5. Add mapping template. Here is a sample template that I've found useful:

```
{
"body" : $input.json('$'),
"headers": {
  #foreach($header in $input.params().header.keySet())
  "$header": "$util.escapeJavaScript($input.params().header.get($header))" #if($foreach.hasNext),#end

  #end
  },
"method": "$context.httpMethod",
"params": {
  #foreach($param in $input.params().path.keySet())
  "$param": "$util.escapeJavaScript($input.params().path.get($param))" #if($foreach.hasNext),#end

  #end
  },
"query": {
  #foreach($queryParam in $input.params().querystring.keySet())
  "$queryParam": "$util.escapeJavaScript($input.params().querystring.get($queryParam))" #if($foreach.hasNext),#end

  #end
  }  
}
```

### For Integration Response

  1.  In API Gateway, select the API you specified when creating the Lamdba function
  2.  Select the GET Method for your new lambda function and select Method Response
  3.  Expand 200 Response and the click on Add Header under Response Headers for 200
  4.  Enter "Content-Type" in the box and click on the check icon to the right
  5.  Select the GET Method again from your lambda function on the left side
  6.  Select Integration Response and expand 200 to add a new mapping to the
      Content-Type Response Header.
  7.  Select the pencil icon to the right and set the Mapping value to:   
      'text/html' (be sure to use single quotes). Save you edit.
  8.  Expand the Mapping Template section and delete the "application/json" content type
  9.  Select "Add mapping template" and enter "text/html" (without quotes).
  10. Select the "text/html" Content Type and set the template value to:

```
  #set($inputRoot = $input.path('$'))
  $inputRoot
```
