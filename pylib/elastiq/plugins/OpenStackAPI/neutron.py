import pycurl
import json
import logging
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from utilities import slash

from instance import Instance
from flavor import Flavor
from image import Image
from keypair import KeyPair
from network import Network

class NeutronAPI:
    def __init__(self):
        self.url=None
        self.tenant_id=None
        self.curl=pycurl.Curl()
        self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        self.curl.setopt(pycurl.SSL_VERIFYHOST, 0)

    #NETWORKS
    def get_networks_list(self, **params):
        min_params=["token_id"]    
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)
        url=str(self.url+"networks")

        self.curl.setopt(pycurl.URL, url)

        headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
        self.curl.setopt(pycurl.HTTPHEADER, headers)
        
        self.curl.setopt(pycurl.POST, 0)
        
        buffer = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

        self.curl.perform()

        body=buffer.getvalue()
        out=json.loads(body)

        networks=[]
        for n in out["networks"]:            
            networks.append(Network(n))

        return networks

    def get_network(self, **params):
        min_params=["token_id", "network_name"]
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)  

        networks=self.get_networks_list(token_id=params["token_id"])
        
        for n in networks:
            if n.name == params["network_name"]:
                return n

        return None
            

