from .base import BehaviourInterface
from .tor import TorBehaviour
from .noProxy import NoProxyBehaviour
import time
import logging as log
import random


class MixTorNoProxyBehaviour(BehaviourInterface):
    requestsNumber = 0

    def __init__(self):
        """
        Populate these properties with proper information
        """
        self.behaviours = [
            TorBehaviour(),
            NoProxyBehaviour()
        ]

    def getProxy(self):
        behaviour:BehaviourInterface = random.choice(self.behaviours)
        return behaviour.getProxy()

    def getUserAgent(self):
        return None

    def changeIdentity(self):
        return None

    def countRequest(self):
        type(self).requestsNumber += 1