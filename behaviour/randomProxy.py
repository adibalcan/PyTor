from .base import BehaviourInterface
import time
import logging as log
import random


class RandomBehaviour(BehaviourInterface):
    requestsNumber = 0

    def __init__(self):
        """
        Populate these properties with proper information
        """
        self.proxyUser = ""
        self.proxyPass = ""
        self.proxyList = [

        ]

    def getProxy(self):
        proxy = self.proxyList[random.randint(0, len(self.proxyList)-1)]
        schema = BehaviourInterface.getProxySchema()

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
        return selectedProxy

    def getUserAgent(self):
        return None

    def changeIdentity(self):
        return None

    def countRequest(self):
        type(self).requestsNumber += 1
