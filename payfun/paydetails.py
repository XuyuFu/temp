import collections
import requests
import json


def paydetails(payKey):
    headers = {
        # The first three are from my developer account
        "X-PAYPAL-SECURITY-USERID": "fuxuyu-facilitator_api1.outlook.com",
        "X-PAYPAL-SECURITY-PASSWORD": "6ZHB6JE9BTCBAYNC",
        "X-PAYPAL-SECURITY-SIGNATURE": "AXiMFXRWkmt9OxNFdW5tF1mgblXiAZX-YRw5Yxc3XZpxdOy0wqWoiX0o",
        "X-PAYPAL-APPLICATION-ID": "APP-80W284485P519543T",
        "X-PAYPAL-SERVICE-VERSION": "1.1.0",
        "X-PAYPAL-REQUEST-DATA-FORMAT": "JSON",
        "X-PAYPAL-RESPONSE-DATA-FORMAT": "JSON"
    }

    params = collections.OrderedDict()
    params = {
        "payKey": payKey,
        "requestEnvelope": {
            "errorLanguage": "en_US",
            "detailLevel": "ReturnAll"  # Error detail level
        }
    }

    url = "https://svcs.sandbox.paypal.com/AdaptivePayments/PaymentDetails"
    response = requests.post(url, data=json.dumps(params), headers=headers)

    response_string = response.content.decode("utf-8")
    response_dict = json.loads(response_string)
    sender = response_dict.get("senderEmail")

    return sender
