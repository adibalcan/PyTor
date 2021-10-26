import abc


class BehaviourInterface(metaclass=abc.ABCMeta):
    """
    Interface implemented based on:
    https://realpython.com/python-interface/#using-abstract-method-declaration
    """
    @classmethod
    def __subclasshook__(cls, subclass):
        methods = ['getProxy',
                   'getUserAgent',
                   'changeIdentity']
        for method in methods:
            if not hasattr(subclass, 'load_data_source'):
                return NotImplemented
        return True

    @staticmethod
    def __getUrllib3Version():
        version = ""
        try:
            import urllib3
            version = urllib3.__version__
        except ImportError as e:
            pass  # module doesn't exists
        return version

    @staticmethod
    def __versionTuple(v):
        """
        Compare two version strings in a very simple manner
        """
        filled = []
        for point in v.split("."):
            filled.append(point.zfill(8))
        return tuple(filled)

    @classmethod
    def getProxySchema(self):
        """
        Sometimes we get proxy handling error. Details at the following link:
        https://stackoverflow.com/questions/66642705/why-requests-raise-this-exception-check-hostname-requires-server-hostname
        """
        urllibVersion = self.__getUrllib3Version()
        schema = {
            "http": "http",
            "https": "http" if urllibVersion and self.__versionTuple(urllibVersion) > self.__versionTuple("1.25.11") else "https"
        }
        return schema

    @abc.abstractmethod
    def getProxy(self):
        """Load in the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def getUserAgent(self):
        """Extract text from the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def changeIdentity(self):
        """Extract text from the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def countRequest(self):
        """Extract text from the data set"""
        raise NotImplementedError