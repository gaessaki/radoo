import logging

import requests
import json

_logger = logging.getLogger(__name__)

AF_KEY = 'lIqfF9Q02VsSSZkwIysfy7i5dzkjwXmem7k1oMdzi0nYAzFucRBKUg=='
TIMEOUT = '15'
API_URL = 'http://host.docker.internal:7071/api/'
# API_URL = 'https://tatsoi.azurewebsites.net/api/'

class RadishApi:
    def __init__(self, path, af_key=AF_KEY, debug_logging=None):
        self.af_key = af_key
        self.base_url = API_URL + path

        def debug_logging_wrapper(xml_string, func):
            _logger.debug('%s: %s', func, xml_string)
            if debug_logging:
                debug_logging(xml_string, func)

        self.debug_logging = debug_logging_wrapper

    def request(self, method, path, data, merchant_key = None):
        headers = {
            "Content-Type":     "application/json",
            "x-functions-key":  self.af_key,
            "timeout":          TIMEOUT
        }

        if merchant_key:
            headers['merchant-key'] = merchant_key

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
    
    def get(self, path, merchant_key = None):
        return self.request('get', path, None, merchant_key)
    
    def post(self, path, data, merchant_key = None):
        return self.request('post', path, data, merchant_key)