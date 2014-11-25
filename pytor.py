import requests
import datetime
import time

from stem import Signal
from stem.control import Controller

showIp = True
maxRetry = 99
maxRequestsPerIP = 0 # 0 means disabled
password = ''
invalidStringList = []
minSourceLength = 200

requestsNumber = 0
changeID = 0

def newId():
    global changeID, password
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password = password)
        controller.signal(Signal.NEWNYM)
    time.sleep(3)
    changeID = 0

def isInvalid(source):
    global invalidStringList, minSourceLength
    if len(source) < minSourceLength:
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
    global headers, proxies
    r = requests.get('http://ifconfig.me/ip', headers = headers, proxies = proxies)
    return r.text

def getSource(url):
    global requestsNumber, changeID, showIp, headers, proxies, maxRetry
        
    if maxRequestsPerIP != 0 and requestsNumber > maxRequestsPerIP:
        print('GET NEW ID, BECAUSE HAS REACHED ', maxRequestsPerIP,' REQUESTS')
        try:
            if changeID == 1:
                time.sleep(6)
            else:
                changeID = 1
                newId()

            requestsNumber = 0
            time.sleep(1)
        except Exception as e:
            print('Exception at proxy change')

    responseText = ''
    retry = 0
    while retry == 0 or internalInvalid(responseText) or isInvalid(responseText):
        try:
            if showIp:
                print('IP ', getIp())
            if url.endswith('.gz'):
                r = requests.get(url, headers = headers, proxies = proxies, stream = True)
                responseText = r.raw.read()
                responseText = gzip.decompress(responseText)
                responseText = responseText.decode("utf-8")
            else:
                r = requests.get(url, headers = headers, proxies = proxies)
                responseText = r.text

            requestsNumber = requestsNumber + 1
            
        except Exception as e:
            print('Exception at request send')

        internalInvalidFlag = False
        if internalInvalid(responseText):
            print('RESPONSE IS INTERNAL INVALID')
            internalInvalidFlag = True
            time.sleep(6)
               
        if internalInvalidFlag == False and isInvalid(responseText):
            print('RETRY WITH NEW ID, BECAUSE RESPONSE IS INVALID')
            try:
                if changeID == 1:
                    time.sleep(6)
                else:
                    changeID = 1
                    newId()

                requestsNumber = 0
            except Exception as e:
                print('Exception at proxy change')
            time.sleep(1)
        if retry > maxRetry:
            print('OVER MAX Retry')
            break
        retry = retry + 1
          
    return responseText