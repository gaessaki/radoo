import logging

import requests
import json

_logger = logging.getLogger(__name__)

AF_KEY = 'lIqfF9Q02VsSSZkwIysfy7i5dzkjwXmem7k1oMdzi0nYAzFucRBKUg=='
TIMEOUT = '15'
API_URL = 'http://host.docker.internal:7071/api/'
# API_URL = 'https://tatsoi.azurewebsites.net/api/'

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

    def request(self, method, path, data):
        headers = {
            "Content-Type":     "application/json",
            "x-functions-key":  self.af_key,
            "timeout":          TIMEOUT
        }

        if self.merchant_key:
            headers['merchant-key'] = self.merchant_key

        url = self.base_url + path

        if data:
            json_data = json.dumps(data)
        else:
            json_data = None

        response = requests.request(
            method,
            url,
            data=json_data,
            headers=headers
        )
        if response is None:
            raise Exception("No response")
        
        if response.status_code < 200 or response.status_code > 299:
            raise Exception(response.status_code, response.text)
        self.debug_logging("Response is %s" % response.text, "%s %s" % (method, path))
        if response.text:
            return response.json()
        return None
    
    def get(self, path):
        return self.request('get', path, None)
    
    def post(self, path, data):
        return self.request('post', path, data)