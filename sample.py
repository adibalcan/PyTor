from pytor import pytor

# Use here, password from tor configuration
pytor.password = 'test'

# Automatically change the IP address if one of those strings are met in http response
pytor.invalidStringList = ['Sorry, you\'re not allowed to access this page.', 'One more step']

# Get source :)
print(pytor.get('https://google.com').text)