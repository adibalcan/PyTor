PyTor
=========
PyTor is a wrapper for requests python module that injects and controls a proxy obtained from Tor network or from a proxy list.

PyTor change automatically the IP address and retry when a string marker is detected in response to a request.  

Requirements
=========
Tor,

Privoxy 

Below you will find how to configure each of them

Installation
=========
ATENTION: First install pip and git

	pip install git+git://github.com/adibalcan/PyTor.git@master

Usage
=========
**The basic configuration**

	from pytor import pytor

	# Use here, password from tor configuration
	pytor.behaviour.password='YOURPASSWORD'
	
	# Automatically change the IP address if one of those strings are met in http response
	pytor.invalidStringList = ['Sorry, you\'re not allowed to access this page.', 'One more step']

	# Get source :)
	print(pytor.get('https://google.com').text)

**The advanced configuration**

You can add multiple options like in the following sample:

	from pytor import pytor

	# Use here, password from tor configuration
	pytor.behaviour.password='YOURPASSWORD' 
	
	# Automatically change the IP address if one of those strings are met in http response
	pytor.invalidStringList = ['Sorry, you\'re not allowed to access this page.', 'One more step']

	# Change the IP address if response is shorter then 200 chars
	pytor.minSourceLength = 200 

	# Show IP address at every request 
	pytor.showIp = True

	# Show output messages 
	pytor.silent = False

	# Get source :)
	print(pytor.get('https://google.com').text)

Privoxy configuration
=========
Privoxy's main configuration file is already prepared for Tor, if you are using a default Tor configuration and run it on the same system as Privoxy, you just have to edit the forwarding section and uncomment the next line from /etc/privoxy/config:

	#        forward-socks5t             /     127.0.0.1:9050 .

Tor configuration
=========
Generate a hash password 

	tor --hash-password YOURPASSWORD

Uncomment this line from /etc/tor/torrc 

	ControlPort 9051

Update hash generated above in /etc/tor/torrc 

	HashedControlPassword 16:3C78EB9AB441234760C108BCC7F8CF3138FA14378C116ECD3E9C942E51





