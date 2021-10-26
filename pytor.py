import time
import random
import copy
import logging as log
from urllib.parse import urlparse

from stem import Signal
from stem.control import Controller
import requests
from requests.exceptions import ConnectionError

from behaviour.base import BehaviourInterface
from behaviour.noProxy import NoProxyBehaviour
from behaviour.tor import TorBehaviour


"""
REQUIREMENTS:
requests > 2.10.0
pysocks
"""

class Pytor(object):
    """
    Static properties
    """
    lastDomains = {}

    def __init__(self, sessionEnabled=False, behaviour: BehaviourInterface = None):
        self.showIp = False
        self.silent = False
        self.sessionEnabled = sessionEnabled
        if sessionEnabled:
            self.session = requests.Session()

        self.behaviour = behaviour or NoProxyBehaviour()

        self.maxRetry = 10

        self.invalidStringList = []
        self.minSourceLength = 150

        self.encoding = ''  # if is empty, request will guess the encoding
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'en-US,en;q=0.8,ro;q=0.6',
            'Cache-Control': 'max-age=0',
            # 'Connection':'keep-alive',
            # 'upgrade-insecure-requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        self.useProxy = True

        # Polite requests
        self.politeRequest = False
        self.politeRequestsBreak = 1  # number of seconds

    def getDomain(self, url):
        return urlparse(url).netloc

    def getIp(self):
        """
        There are multiple options for IP checking:
        "https://api.ipify.org/"
        "https://httpbin.org/ip"
        """
        r = requests.get('https://httpbin.org/ip', proxies=self.behaviour.getProxy(), headers=self.headers)
        return r.text

    def displayIp(self):
        if self.showIp:
            try:
                log.info('Public IP address ' + self.getIp())
            except:
                log.exception("Exception on procuring IP from API")

    def checkValidity(self, response):
        source = response.text
        reasons = []
        valid = True
        if self.minSourceLength != 0 and len(source) < self.minSourceLength:
            valid = False
            reasons.append({
                'type': 'min_source',
                'message': 'source length is less than {} chars'.format(self.minSourceLength)
            })
        if 'privoxy' in source.lower():
            valid = False
            reasons.append({
                'type': 'internal',
                'message': '"privoxy" word was found in source. Please check privoxy'
            })
        if response.status_code == 403:
            valid = False
            reasons.append({
                'type': 'status',
                'message': '{} status code response'.format(response.status_code)
            })
        for invalidString in self.invalidStringList:
            if invalidString.lower() in source.lower():
                valid = False
                reasons.append({
                    'type': 'keywords',
                    'message': 'keyword "{}" was found'.format(invalidString)
                })
        return valid, reasons

    def waitForPoliteRequest(self, url):
        if self.politeRequest:
            domain = self.getDomain(url)
            while domain in type(self).lastDomains and \
                    time.time() - type(self).lastDomains[domain] < self.politeRequestsBreak:
                log.info("Let's take a break for domain: {}".format(domain))
                time.sleep(self.politeRequestsBreak)
            type(self).lastDomains[domain] = time.time()

    def checkAndRetry(self, requestsMethod, url, **kwargs):
        self.waitForPoliteRequest(url)
        response = None
        for retry in range(1, self.maxRetry+1):
            try:
                if self.useProxy:
                    proxy = self.behaviour.getProxy()
                    if proxy:
                        kwargs["proxies"] = self.behaviour.getProxy()

                response = requestsMethod(url, **kwargs)
                self.behaviour.countRequest()

                # set encoding if exists
                if self.encoding:
                    response.encoding = self.encoding

                valid, reasons = self.checkValidity(response)
                if valid:
                    break  # success exit
                else:
                    for reason in reasons:
                        log.warning('Retry {}/{} reason: {}'.format(retry, self.maxRetry, reason['message']))
                        if reason['type'] == 'internal':
                            time.sleep(6)
                        elif reason['type'] in ['min_source', 'keywords']:
                            self.behaviour.changeIdentity()
                            break
                        else:
                            self.behaviour.changeIdentity()
                            break
            except ConnectionError as e:
                log.exception('Connexion exception')
            except Exception as e:
                log.exception('Exception at request send')
        return response

    def __getattr__(self, name):
        """
        Catch all requests methods GET, POST, PUT, DELETE.
        name parameter contains one of the above method OR one class attribute
        """
        try:
            return object.__getattr__(self, name)
        except AttributeError:
            def handlerFunction(*args, **kwargs):
                requestsMethod = getattr(self.session, name) if self.sessionEnabled else getattr(requests, name)
                url = args[0]

                # force encoding from requests
                if 'encoding' in kwargs:
                    self.encoding = kwargs.pop('encoding')

                defaultParams = {
                    "headers": self.headers,
                    "proxies": self.getProxy(),
                    "timeout": (60, 60)  # connection and read timeout
                }
                params = copy.deepcopy(defaultParams)
                params.update(kwargs)

                # Send and validate initial request
                return self.checkAndRetry(requestsMethod, url, **params)

            return handlerFunction


pytor = Pytor(behaviour=TorBehaviour())

if __name__ == '__main__':
    pytor.password = 'test'
    print(pytor.post("http://httpbin.org/post", data={"test": "test"}).text, flush=True)
    pytor.newId()
    for i in range(10):
        print(pytor.get("http://httpbin.org/get").text, flush=True)
