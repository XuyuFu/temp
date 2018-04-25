
import collections
import requests
import json
from .paydetails import paydetails

def trans(recipient_email, dollars):

    headers = {
        #The first three are from my developer account
        "X-PAYPAL-SECURITY-USERID":"fuxuyu-facilitator_api1.outlook.com",
        "X-PAYPAL-SECURITY-PASSWORD":"6ZHB6JE9BTCBAYNC",
        "X-PAYPAL-SECURITY-SIGNATURE":"AXiMFXRWkmt9OxNFdW5tF1mgblXiAZX-YRw5Yxc3XZpxdOy0wqWoiX0o",
        "X-PAYPAL-APPLICATION-ID": "APP-80W284485P519543T",
        "X-PAYPAL-SERVICE-VERSION":"1.1.0",
        "X-PAYPAL-REQUEST-DATA-FORMAT":"JSON",
        "X-PAYPAL-RESPONSE-DATA-FORMAT":"JSON"
    }

    # Store your paypal credentials in a separate file (my example:
    # "credentials.json" in paypal_project folder) and add that file to .gitignore.
    # Retrieve credentials like so:

    params = collections.OrderedDict()
    params = {
        "senderEmail": "fuxuyu-facilitator@outlook.com",
        "actionType":"PAY",    #Specify the payment action
        "currencyCode":"USD",
        "receiverList":{"receiver":[{
        "amount":"",
        "email":""}]  # The payment Receiver's email address
    },
        # Where the Sender is redirected to after approving a successful payment
        "returnUrl":"http://127.0.0.1:8000",
        # Where the Sender is redirected to upon a canceled payment
        "cancelUrl":"http://127.0.0.1:8000",
        "requestEnvelope":{
        "errorLanguage":"en_US",
        "detailLevel":"ReturnAll"   # Error detail level
    }
    }

    # Assign recipients email and paid amount in dollars to appropriate params:
    params["receiverList"]["receiver"][0]["email"] = recipient_email
    params["receiverList"]["receiver"][0]["amount"] = str(dollars)

    # Send a Pay request to PayPal
    url = "https://svcs.sandbox.paypal.com/AdaptivePayments/Pay"
    response = requests.post(url, data=json.dumps(params), headers=headers)

    # Check the response:
    #print(response.content.decode())
    response_string = response.content.decode("utf-8")
    response_dict = json.loads(response_string)
    print("the response dic", response_dict)
    payKey = response_dict.get("payKey")
    print("the payKey: ", payKey)
    
    paypal_redirect_string = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey=" + payKey
    return paypal_redirect_string