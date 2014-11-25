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

	pytor.password='test'
	pytor.invalidStringList = ['Sorry, you\'re not allowed to access this page.', 'One more step'] 
	print(pytor.getSource('http://thewebminer.com'))


