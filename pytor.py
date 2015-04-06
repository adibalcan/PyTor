import requests
import datetime
import time
import gzip

from stem import Signal
from stem.control import Controller

# CONFIG
showIp = False
silent = False
maxRetry = 10
maxRequestsPerIP = 100 # 0 means disabled
password = ''
invalidStringList = []
minSourceLength = 200 # 0 means disabled

#internal globals
requestsNumber = 0
changeIDInPregress = False

def output(str):
    if not silent:
        print(str)

def newId():
    global changeIDInPregress
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password = password)
        controller.signal(Signal.NEWNYM)
    time.sleep(3)
    changeIDInPregress = False

def isInvalid(source):
    if minSourceLength != 0 and len(source) < minSourceLength:
        return True
    for string in invalidStringList:
        if string in source:
            return True
    return False

def internalInvalid(source):
    if 'Privoxy' in source:
        return True
    return False

#Connect to Tor by Privoxy
proxies = {
                'http': 'http://127.0.0.1:8118',
                'https': 'https://127.0.0.1:8118'
            }
headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip,deflate,sdch',
            'Accept-Language':'en-US,en;q=0.8,ro;q=0.6',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36',
            }

def getIp():
    r = requests.get('http://ifconfig.me/ip', headers = headers, proxies = proxies)
    return r.text

def getSource(url):
    global requestsNumber, changeIDInPregress
        
    if maxRequestsPerIP != 0 and requestsNumber > maxRequestsPerIP:
        output('GET NEW ID, BECAUSE HAS REACHED ' + str(maxRequestsPerIP) + ' REQUESTS')
        try:
            if changeIDInPregress:
                time.sleep(6)
            else:
                changeIDInPregress = True
                newId()

            requestsNumber = 0
            time.sleep(1)
        except Exception as e:
            output('Exception at proxy change')

    responseText = ''
    retry = 0
    while retry == 0 or internalInvalid(responseText) or isInvalid(responseText):
        try:
            if showIp:
                output('IP address ' + getIp())
            if url.endswith('.gz'):
                r = requests.get(url, headers = headers, proxies = proxies, stream = True)
                responseText = r.raw.read()
                responseText = gzip.decompress(responseText)
                responseText = responseText.decode("utf-8")
            else:
                r = requests.get(url, headers = headers, proxies = proxies)
                responseText = r.text

            requestsNumber += 1
            
        except Exception as e:
            output('Exception at request send')

        internalInvalidFlag = False
        if internalInvalid(responseText):
            output('RESPONSE IS INTERNAL INVALID')
            internalInvalidFlag = True
            time.sleep(6)
               
        if internalInvalidFlag == False and isInvalid(responseText):
            output('RETRY WITH NEW ID, BECAUSE RESPONSE IS INVALID')
            try:
                if changeIDInPregress:
                    time.sleep(6)
                else:
                    changeIDInPregress = True
                    newId()

                requestsNumber = 0
            except Exception as e:
                output('Exception at proxy change')
            time.sleep(1)
        if retry > maxRetry:
            output('OVER MAX Retry')
            break
        retry += 1         
    return responseText