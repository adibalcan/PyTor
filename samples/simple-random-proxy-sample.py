from pytor import pytor

from behaviour.randomProxy import RandomBehaviour
random = RandomBehaviour()
random.proxyList = []  # list with proxies strings as ip addresses with ports
random.proxyUser = ""
random.proxyPass = ""

pytor.behaviour = random

# Automatically change the IP address if one of those strings are met in http response
pytor.invalidStringList = ['Sorry, you\'re not allowed to access this page.', 'One more step']

# Get source which contains your IP address :)
print(pytor.getIp())

# Change the identity and check again the IP address
pytor.behaviour.changeIdentity()
print(pytor.getIp())