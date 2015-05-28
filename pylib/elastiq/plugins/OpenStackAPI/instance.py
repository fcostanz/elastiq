import pycurl
import json
import time
import logging
import sys

from openStackObject import OpenStackObject

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

class Instance(OpenStackObject):
    def __init__(self, info=None):
        self.reset()

        self.curl=pycurl.Curl()
        self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        self.curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        if info is not None:
            self.update(info=info)
        
    def reset(self):
        self.id=None
        self.name=None
        self.user_id=None
        self.url=None
        self.addresses=[]
        self.image_id=None
        self.flavor_id=None
        self.tenant_id=None
        self.key_name=None

    def update(self, **params):
        if "token_id" in params.keys():
            self.curl.setopt(pycurl.URL, self.url)
            
            headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
            self.curl.setopt(pycurl.HTTPHEADER, headers)
            
            self.curl.setopt(pycurl.POST, 0)
            
            buffer = StringIO()
            self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            
            self.curl.perform()
            
            body=buffer.getvalue()
            info=json.loads(body)["server"]

        else:
            try:
                info=params["info"]
            except KeyError:
                logging.warning("Non possible to update instance info.")
                return None

        self.id=info["id"]
        self.name=info["name"]
        self.user_id=info["user_id"]
        for link in info["links"]:
            if link["rel"]=="self":
                self.url=str(link["href"])
        self.addresses=info["addresses"]
        self.image_id=info["image"]["id"]
        self.flavor_id=info["flavor"]["id"]
        self.tenant_id=info["tenant_id"]
        self.key_name=info["key_name"]

    def network_ip(self, **params):
        try:
            return self.addresses[params["network_name"]][0]["addr"]
        except:
            return None
    
    def status(self, **params):
        min_params=["token_id"]    
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)
     
        self.curl.setopt(pycurl.URL, self.url)

        headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
        self.curl.setopt(pycurl.HTTPHEADER, headers)
        
        self.curl.setopt(pycurl.POST, 0)
        
        buffer = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

        self.curl.perform()

        body=buffer.getvalue()
        out=json.loads(body)["server"]

        if out["status"].lower() == "active":
            return "running"

        return out["status"].lower()


    def terminate(self, **params):
        min_params=["token_id"]    
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)
     
        self.curl.setopt(pycurl.URL, self.url)

        headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
        self.curl.setopt(pycurl.HTTPHEADER, headers)
        
        self.curl.setopt(pycurl.POST, 0)
        self.curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")

        self.curl.perform()

        self.curl.unsetopt(pycurl.CUSTOMREQUEST)
