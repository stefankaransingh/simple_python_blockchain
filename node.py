from urlparse import urlparse

class Node(object):

    def __init__(self,address=None):
        self.url = urlparse(address)

    def get_network_location(self):
        return self.url.netloc
