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

class NovaAPI:
    def __init__(self):
        self.url=None
        self.tenant_id=None
        self.curl=pycurl.Curl()
        self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        self.curl.setopt(pycurl.SSL_VERIFYHOST, 0)

    #INSTANCES
    def get_instances_list(self, **params):
        min_params=["token_id"]    
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)
        
        try:
            url=str(self.url+params["tenant_id"]+"/servers/detail")
        except KeyError:
            url=str(self.url+self.tenant_id+"/servers/detail")

        self.curl.setopt(pycurl.URL, url)

        headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
        self.curl.setopt(pycurl.HTTPHEADER, headers)
        
        self.curl.setopt(pycurl.POST, 0)
        
        buffer = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

        self.curl.perform()

        body=buffer.getvalue()
        out=json.loads(body)

        instances=[]
        for i in out["servers"]:            
            instances.append(Instance(i))

        return instances

    def get_instance(self, **params):
        min_params=["token_id", "instance_id"]
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)  
        
        try:
            instances=self.get_instances_list(token_id=params["token_id"], tenant_id=params["tenant_id"])
        except KeyError:
            instances=self.get_instances_list(token_id=params["token_id"])            
        
        for i in instances:
            if i.id == params["instance_id"]:
                return i

        return None
            
    #FLAVORS
    def get_flavors_list(self, **params):
        min_params=["token_id", "tenant_id"]    
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)
    
        url=str(self.url+params["tenant_id"]+"/flavors/detail")
        self.curl.setopt(pycurl.URL, url)

        headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
        self.curl.setopt(pycurl.HTTPHEADER, headers)
        
        self.curl.setopt(pycurl.POST, 0)
        
        buffer = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

        self.curl.perform()

        body=buffer.getvalue()
        out=json.loads(body)

        flavors=[]
        for f in out["flavors"]:            
            flavors.append(Flavor(f))

        return flavors

    def get_flavor(self, **params):
        min_params=["token_id", "tenant_id", "flavor_name"]
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)  

        flavors=self.get_flavors_list(token_id=params["token_id"], tenant_id=params["tenant_id"])
        
        for f in flavors:
            if f.name == params["flavor_name"]:
                return f

        return None
            
    #IMAGES
    def get_images_list(self, **params):
        min_params=["token_id"]    
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of images", p)
                sys.exit(3)
    
        try:
            url=str(self.url+params["tenant_id"]+"/images/detail")
        except KeyError:
            url=str(self.url+self.tenant_id+"/images/detail")
        self.curl.setopt(pycurl.URL, url)

        headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
        self.curl.setopt(pycurl.HTTPHEADER, headers)
        
        self.curl.setopt(pycurl.POST, 0)
        
        buffer = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

        self.curl.perform()

        body=buffer.getvalue()
        out=json.loads(body)
        
        images=[]
        for i in out["images"]:
            images.append(Image(i))

        return images

    def get_image(self, **params):
        min_params=["token_id", "tenant_id", "image_id"]
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)  

        images=self.get_images_list(token_id=params["token_id"], tenant_id=params["tenant_id"])
        
        for i in images:
            if i.id == params["image_id"]:
                return i

        return None

    #KEYPAIRS
    def get_keypairs_list(self, **params):
        min_params=["token_id", "tenant_id"]    
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)
    
        url=str(self.url+params["tenant_id"]+"/os-keypairs")
        self.curl.setopt(pycurl.URL, url)

        headers = ["Content-Type:application/json","X-Auth-Token:"+params["token_id"]]
        self.curl.setopt(pycurl.HTTPHEADER, headers)
        
        self.curl.setopt(pycurl.POST, 0)
        
        buffer = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

        self.curl.perform()

        body=buffer.getvalue()
        out=json.loads(body)

        keypairs=[]
        for k in out["keypairs"]:
            keypairs.append(KeyPair(k["keypair"]))

        return keypairs

    def get_keypair(self, **params):
        min_params=["token_id", "tenant_id", "keypair_name"]
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to retrieve list of instances", p)
                sys.exit(3)  

        keypairs=self.get_keypairs_list(token_id=params["token_id"], tenant_id=params["tenant_id"])
        
        for k in keypairs:
            if k.name == params["keypair_name"]:
                return k

        return None
