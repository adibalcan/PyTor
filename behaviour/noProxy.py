from .base import BehaviourInterface
import time
import logging as log


class NoProxyBehaviour(BehaviourInterface):
    requestsNumber = 0

    def getProxy(self):
        return None

    def getUserAgent(self):
        return None

    def changeIdentity(self):
        return None

    def countRequest(self):
        type(self).requestsNumber += 1
