import pycurl
import json
import time

import logging

from openStackObject import OpenStackObject

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO


class Flavor(OpenStackObject):
    def __init__(self, info=None):
        if info is None:
            self.id=None
            self.name=None
            self.url=None
        else:
            self.id=info["id"]
            self.name=info["name"]
            for link in info["links"]:
                if link["rel"]=="self":
                    self.url=str(link["href"])
