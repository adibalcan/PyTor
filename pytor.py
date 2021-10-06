import time
import random
import copy
import logging as log
from urllib.parse import urlparse

from stem import Signal
from stem.control import Controller
import requests
from requests.exceptions import ConnectionError


"""
REQUIREMENTS:
requests > 2.10.0
pysocks
"""

class Pytor(object):
    """
    Static properties
    """
    proxyListCursor = 0
    changeIdInProgress = False
    lastDomains = {}

    def __init__(self, sessionEnabled=False):
        self.showIp = False
        self.silent = False
        self.sessionEnabled = sessionEnabled
        if sessionEnabled:
            self.session = requests.Session()
        self.maxRetry = 10
        self.maxRequestsPerIP = 100  # for tor
        self.password = ''
        self.invalidStringList = []
        self.minSourceLength = 150
        self.controlPort = 9051
        self.torPort = 9050
        self.country = ''
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
        # Connect to Tor by Privoxy
        self.proxies = {
            'http': '127.0.0.1:8118',
            'https': '127.0.0.1:8118'
        }
        """
        Connect directly to TOR
        requires requests > 2.10.0
        self.proxies = {
            'http': 'socks4a://127.0.0.1:9050',
            'https': 'socks4a://127.0.0.1:9050'
        }
        """

        self.rotatingProxies = False
        self.proxyList = []  # Add your proxy list here
        self.proxyUser = ""
        self.proxyPass = ""

        if self.rotatingProxies:
            type(self).proxyListCursor = random.randint(0, len(self.proxyList) - 1)

        # Polite requests
        self.politeRequest = False
        self.politeRequestsBreak = 1  # nuber of seconds

        # Internal globals
        self.requestsNumber = 0

    def getDomain(self, url):
        return urlparse(url).netloc

    def getIp(self):
        """
        There are multiple options for IP checking:
        "https://api.ipify.org/"
        "https://httpbin.org/ip"
        """
        r = requests.get('https://httpbin.org/ip', proxies=self.proxies, headers=self.headers)
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

    def newId(self):
        """
        TODO: move in a behaviour class
        """
        if type(self).changeIdInProgress:
            time.sleep(6)
        else:
            type(self).changeIdInProgress = True
            try:
                with Controller.from_port(port=self.controlPort) as controller:
                    controller.authenticate(password=self.password)
                    controller.signal(Signal.NEWNYM)
                    '''
                    Wait until newnym signal is ready
                    https://stem.torproject.org/api/control.html#stem.control.Controller.get_newnym_wait 
                    '''
                    time.sleep(controller.get_newnym_wait())
            except Exception as e:
                log.exception('Exception at proxy change')

            self.requestsNumber = 0
            type(self).changeIdInProgress = False

    def checkMaxLimit(self):
        """
        TODO: move in a behaviour class
        """
        if not self.rotatingProxies:
            if self.maxRequestsPerIP != 0 and self.requestsNumber > self.maxRequestsPerIP:
                log.info('GET NEW ID, BECAUSE HAS REACHED ' + str(self.maxRequestsPerIP) + ' REQUESTS')
                self.newId()

    @staticmethod
    def __getUrllib3Version():
        version = ""
        try:
            import urllib3
            version = urllib3.__version__
        except ImportError as e:
            pass  # module doesn't exists
        return version

    @staticmethod
    def __versionTuple(v):
        """
        Compare two version strings in a very simple manner
        """
        filled = []
        for point in v.split("."):
            filled.append(point.zfill(8))
        return tuple(filled)

    def getProxy(self):
        """
        TODO: move in a behaviour class
        Sometimes we get proxy handling error. Details at the following link:
        https://stackoverflow.com/questions/66642705/why-requests-raise-this-exception-check-hostname-requires-server-hostname
        """
        urllibVersion = self.__getUrllib3Version()
        schema = {
            "http": "http",
            "https": "http" if urllibVersion and self.__versionTuple(urllibVersion) > self.__versionTuple("1.25.11") else "https"
        }

        if self.rotatingProxies:
            proxy = self.proxyList[self.proxyListCursor]
            selectedProxy = {
                "http": "{schema}://{user}:{password}@{proxy}".format(schema=schema["http"],
                                                                      user=self.proxyUser,
                                                                      password=self.proxyPass,
                                                                      proxy=proxy),

                "https": "{schema}://{user}:{password}@{proxy}".format(schema=schema["https"],
                                                                       user=self.proxyUser,
                                                                       password=self.proxyPass,
                                                                       proxy=proxy)
            }

            if type(self).proxyListCursor < len(self.proxyList) - 1:
                type(self).proxyListCursor += 1
            else:
                type(self).proxyListCursor = 0
        elif self.useProxy:
            selectedProxy = {
                "http": "{schema}://{proxy}".format(schema=schema["http"], proxy=self.proxies["http"]),
                "https": "{schema}://{proxy}".format(schema=schema["https"], proxy=self.proxies["https"])
            }
        else:
            selectedProxy = {}
        return selectedProxy

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
                    kwargs["proxies"] = self.getProxy()

                response = requestsMethod(url, **kwargs)
                self.requestsNumber += 1

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
                            self.newId()
                            break
                        else:
                            self.newId()
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


pytor = Pytor()

if __name__ == '__main__':
    pytor.password = 'test'
    print(pytor.post("http://httpbin.org/post", data={"test": "test"}).text, flush=True)
    pytor.newId()
    for i in range(10):
        print(pytor.get("http://httpbin.org/get").text, flush=True)
