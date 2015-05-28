from utilities import slash

import pycurl
import json
import time
import logging

from openStackObject import OpenStackObject

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

class Network(OpenStackObject):
    def __init__(self, info=None):
        if info is None:
            self.id=None
            self.name=None
            self.tenant_id=None
        else:
            self.id=info["id"]
            self.name=info["name"]
            self.tenant_id=info["tenant_id"]

        self.curl=pycurl.Curl()
        self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        self.curl.setopt(pycurl.SSL_VERIFYHOST, 0)

    def status(self, **params):
        min_params=["token_id", "server_url"]
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)
     
        self.curl.setopt(pycurl.URL, str(slash(params["server_url"])+"networks/"+self.id))

        headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
        self.curl.setopt(pycurl.HTTPHEADER, headers)
        
        self.curl.setopt(pycurl.POST, 0)
        
        buffer = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

        self.curl.perform()

        body=buffer.getvalue()
        out=json.loads(body)["network"]

        return out["status"].lower()
