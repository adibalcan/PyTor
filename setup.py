from distutils.core import setup
setup(name='pytor',
      version='1.3',
      py_modules=['pytor'],
      install_requires=[
          'stem',
          'requests',
      ],
      description='Python module for http requests by tor network',
      keywords='tor proxy http requests',
      author='Adrian Balcan',
      author_email='adrian@thewebminer.com'
      )