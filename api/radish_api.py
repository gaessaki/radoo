import json
import logging
from odoo.tools.translate import _lt

import requests
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

AF_KEY = 'lIqfF9Q02VsSSZkwIysfy7i5dzkjwXmem7k1oMdzi0nYAzFucRBKUg=='
TIMEOUT = '15'
API_URL = 'https://tatsoi.azurewebsites.net/api/'

API_ERROR_MESSAGES = {
    'InvalidMerchantKey':               _lt('No merchant key was provided. Please ensure that a key is configured for the current environment.'),
    'MerchantKeyNotFound':              _lt('The provided merchant key is invalid. Please check the key and try again.'),
    'MerchantStatusNotActive':          _lt('The provided merchant key is not active. Please contact Radish support.'),
    'MissingOrders':                    _lt('No orders were provided in the request.'),
    'OrderNotFound':                    _lt('No order was found for the provided order reference.'),
    'OrderAlreadyCompleted':            _lt('The order has already been completed and can no longer be modified.'),
    'LowAddressPrecision':              _lt("The provided delivery address could not be verified. Please ensure that all address details are accurate and complete. Delivery instructions should be entered separately from the address fields."),
}

class RadishApi:
    def __init__(self, endpoint, af_key=AF_KEY, merchant_key=None, debug_logging=None):
        self.af_key = af_key
        self.base_url = API_URL + endpoint
        self.merchant_key = merchant_key

        def debug_logging_wrapper(xml_string, func):
            _logger.debug('%s: %s', func, xml_string)
            if debug_logging:
                debug_logging(xml_string, func)

        self.debug_logging = debug_logging_wrapper

    def request(self, method, path, json_data):
        headers = {
            "Content-Type":    "application/json",
            "x-functions-key": self.af_key,
            "timeout":         TIMEOUT
        }

        if self.merchant_key:
            headers['merchant-key'] = self.merchant_key

        url = self.base_url + path
        logged_headers = {k: v for k, v in headers.items() if k != 'x-functions-key'}
        self.debug_logging("Request: %s %s \nHeaders: %s \nPayload: %s" % (method, url, json.dumps(logged_headers, indent=2), json.dumps(json_data, indent=2)),
                           "%s %s" % (method, path))

        try:
            response = requests.request(
                method,
                url,
                json=json_data,
                headers=headers
            )
        except requests.exceptions.RequestException as e:
            self.debug_logging("Request failed", "%s %s" % (method, path))
            raise ValidationError(_lt("Failed to connect to the Radish API Server."))

        content_type = response.headers.get('content-type', None)
        if content_type == 'application/pdf':
            response_text = response.content
        else:
            response_text = response.text

        self.debug_logging("Response is %s" % response_text, "%s %s" % (method, path))

        status_code = response.status_code
        if status_code == 500:
            raise ValidationError(_lt("Internal server error. Please contact Radish support if this problem persists."))
        if status_code != 200:
            try:
                error_message = API_ERROR_MESSAGES.get(response.json().get('error'), response.json().get('error'))
            except Exception:
                error_message = response.text

            raise ValidationError(_lt("Request failed with status code %s : \n%s") % (status_code, error_message))

        return response

    def get(self, path):
        return self.request('get', path, None)

    def post(self, path, data):
        return self.request('post', path, data)
