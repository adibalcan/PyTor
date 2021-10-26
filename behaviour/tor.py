from .base import BehaviourInterface
import time
import logging as log
from stem import Signal
from stem.control import Controller


class TorBehaviour(BehaviourInterface):
    # static properties
    changeIdInProgress = False
    requestsNumber = 0

    def __init__(self):
        self.controlPort = 9051
        self.torPort = 9050
        self.password = 'test'
        self.maxRequestsPerIP = 100

    def getProxy(self):
        """
        Tor connexion to privoxy
        Connect directly to TOR
        requires requests > 2.10.0
        self.proxies = {
            'http': 'socks4a://127.0.0.1:9050',
            'https': 'socks4a://127.0.0.1:9050'
        }
        """
        return {
            'http': '127.0.0.1:8118',
            'https': '127.0.0.1:8118'
        }

    def checkMaxLimit(self):
        """ TODO: use this method at every request """
        if self.maxRequestsPerIP != 0 and self.requestsNumber > self.maxRequestsPerIP:
            log.info('GET NEW ID, BECAUSE HAS REACHED ' + str(self.maxRequestsPerIP) + ' REQUESTS')
            self.changeIdentity()

    def getUserAgent(self):
        return None

    def changeIdentity(self):
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
                type(self).requestsNumber = 0
            except Exception as e:
                log.exception('Exception at proxy change')

            type(self).changeIdInProgress = False

    def countRequest(self):
        type(self).requestsNumber += 1