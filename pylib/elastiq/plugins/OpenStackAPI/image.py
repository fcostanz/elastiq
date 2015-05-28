import pycurl
import json
import logging
import sys
import base64
import time

from utilities import slash

from instance import Instance
from flavor import Flavor
from keypair import KeyPair
from network import Network

from openStackObject import OpenStackObject

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

class Image(OpenStackObject):
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

        self.curl=pycurl.Curl()
        self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        self.curl.setopt(pycurl.SSL_VERIFYHOST, 0)

    def run(self, **params):
        inst_param = {
            "server" : {
                "name" : "oq-worker"+str(int(time.mktime(time.localtime()))),
                "metadata" : {
                    "My Server Name" : "My openquake worker"
                    }
                }
            }

        time.sleep(2)

        inst_param["server"]["imageRef"]=self.id

        try:
            inst_param["server"]["flavorRef"] = params["instance_type"]
        except KeyError:
            logging.error("Flavor missing")
            sys.exit(3)

        try:
            inst_param["server"]["key_name"] = params["key_name"]
        except KeyError:
            logging.warning("Keypair name missing")

        try:
            inst_param["server"]["networks"] = [{"uuid" : params["network"]}]
        except KeyError:
            logging.warning("Network uuid missing")

        try:
            inst_param["server"]["user_data"] = base64.b64encode(params["user_data"])
        except KeyError:
            logging.warning("UserData missing")

        min_params=["token_id"]
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to create instance", p)
                sys.exit(3)
                
        url=self.url[:self.url.rfind("/")]
        url=self.url[:url.rfind("/")]
        url+="/servers"
        self.curl.setopt(pycurl.URL, url)

        headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
        data=json.dumps(inst_param, sort_keys=True)

        self.curl.setopt(pycurl.HTTPHEADER, headers)        
        self.curl.setopt(pycurl.POST, 1)
        self.curl.setopt(pycurl.POSTFIELDS, data)
        
        buffer = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

        self.curl.perform()

        body=buffer.getvalue()
        out=json.loads(body)

        return out["server"]["id"]
