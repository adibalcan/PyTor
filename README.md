PyTor
=========

Python module for http requests by tor network

Requirements
=========
tor,

privoxy

Installation
=========
ATENTION: First install pip and git

	pip install git+git://github.com/adibalcan/PyTor.git@master

Usage
=========
	import pytor

	pytor.password='YOURPASSWORD' # Use here password from tor configuration
	pytor.invalidStringList = ['Sorry, you\'re not allowed to access this page.', 'One more step'] 
	print(pytor.getSource('http://thewebminer.com'))

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





