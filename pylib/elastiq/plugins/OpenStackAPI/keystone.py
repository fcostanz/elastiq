from utilities import slash

import pycurl
import json
import logging
import sys
from datetime import datetime, timedelta

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from utilities import slash

class KeyStoneAPI:
    def __init__(self):
        self.url=None
        self.access=None
        self.curl=None
        self.token_exp_date=None

    def connect(self, **params):
        min_params=["url", "username", "password"]
        
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to establish connection", p)
                sys.exit(3)

        self.url=params["url"]

        try:
            data='{"auth": { "tenantName": "'+params["tenantName"]+'", "passwordCredentials": {"username": "'+params["username"]+'", "password": "'+params["password"]+'"}}}'
        except KeyError:
            data='{"auth": { "passwordCredentials": {"username": "'+params["username"]+'", "password": "'+params["password"]+'"}}}'

        headers = ["Content-Type:application/json"]
        
        c=pycurl.Curl()

        c.setopt(pycurl.URL, self.url+"/tokens")
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
    
        c.setopt(pycurl.POST, 1)
        
        c.setopt(pycurl.HTTPHEADER, headers)
        c.setopt(pycurl.POSTFIELDS, data)

        buffer = StringIO()
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)

        now=datetime.now()
        c.perform()

        self.curl=c

        body=buffer.getvalue()
        self.access=json.loads(body)

        if "error" in self.access.keys():
            logging.error("Authentication error. code: %s, message: %s", self.access["error"]["code"], self.access["error"]["message"])
            sys.exit(3)

        self.convert_token_exp_date(now)

    def renew_token(self, tenantName=None):
        if not self.token_is_valid:
            logging.warning("Token expired on %s", self.token_info["expires"])
            return 1

        c=self.curl

        c.setopt(pycurl.URL, self.url+"/tokens")

        c.setopt(pycurl.POST, 1)
        if tenantName is None:
            data='{"auth": { "token": {"id": "'+self.token_id+'"}}}'
        else:
            data='{"auth": { "tenantName": "'+tenantName+'", "token": {"id": "'+self.token_id+'"}}}'

        c.setopt(pycurl.POSTFIELDS, data)

        buffer = StringIO()
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)

        now=datetime.now()
        c.perform()

        body=buffer.getvalue()
        self.access=json.loads(body)

        if "error" in self.access.keys():
            logging.error("Authentication error. code: %s, message: %s", self.access["error"]["code"], self.access["error"]["message"])
            sys.exit(3)

        self.convert_token_exp_date(now)

    def services(self, tenantName=None):
        if tenantName is None:
            try:
                self.access["access"]["serviceCatalog"]
            except KeyError:
                logging.error("Service catalog not available. Tenant Name needed.")
                sys.exit(3)
        else:
            self.renew_token(tenantName)

    def nova_url(self, tenantName, url=None):
        if url is not None:
            url=slash(url)
            
        if self.access is None:
            logging.error("Impossible to retrieve nova server url. Connect to keystone first.")
            sys.exit(3)

        self.services(tenantName)

        urls=[]
        for s in self.access["access"]["serviceCatalog"]:
            if s["name"]=="nova" and s["type"]=="compute":                
                urls.append(slash(s["endpoints"][0]["publicURL"][:s["endpoints"][0]["publicURL"].rfind('/')]))                
    
        if len(urls)==0:
            logging.error("Nova server not found.")
            sys.exit(3)

        if url is None:
            return urls[0]
        else:
            if url in urls:
                return url
            else:
                logging.warning("Nova server %s not found.", url)
                return None
    
    def neutron_url(self, tenantName, url=None):
        if url is not None:
            url=slash(url)
            
        if self.access is None:
            logging.error("Impossible to retrieve neutron server url. Connect to keystone first.")
            sys.exit(3)

        self.services(tenantName)

        urls=[]        
        for s in self.access["access"]["serviceCatalog"]:
            if s["name"]=="neutron" and s["type"]=="network":
                urls.append(slash(s["endpoints"][0]["publicURL"])+"v2.0/")

        if len(urls)==0:
            logging.error("Neutron server not found.")
            sys.exit(3)

        if url is None:
            return urls[0]
        else:
            if url in urls:
                return url
            else:
                logging.warning("Neutron server %s not found.", url)
                return None

    def tenants(self):
        c=self.curl
        
        c.setopt(pycurl.URL, self.url+"/tenants")
        
        headers = ["Content-Type:application/json","X-Auth-Token:"+self.token_id]
        c.setopt(pycurl.HTTPHEADER, headers)
        
        c.setopt(pycurl.POST, 0)
        
        buffer = StringIO()
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)

        c.perform()
        
        body=buffer.getvalue()
        res=json.loads(body)

        if "error" in res.keys():
            logging.error("Tenants error, code: %s, message: %s", res["error"]["code"], res["error"]["message"])
            sys.exit(3)

        try:
            res["tenants"]
        except KeyError:
            logging.error("Tenants not found")
            sys.exit(3)

        return res

    def tenant_id(self, tenantName):
        tenants=self.tenants()

        for t in tenants["tenants"]:
            if t["name"] == tenantName:
                return t["id"]

        logging.error('Tenant "%s" not found', tenantName)
        sys.exit(3)

    def convert_token_exp_date(self, now=None):
        if now is None:
            now=datetime.now()

        issued=self.token_info["issued_at"]
        issued=issued[:issued.rfind(".")]
        issued_FMT = "%Y-%m-%dT%H:%M:%S"

        exp=self.token_info["expires"]
        exp_FMT= "%Y-%m-%dT%H:%M:%SZ"

        token_validity=datetime.strptime( exp, exp_FMT) - datetime.strptime( issued, issued_FMT)
        self.token_exp_date=now+token_validity

    @property
    def token_id(self):
        if not self.token_is_valid:
            logging.warning("Token expired on %s", self.token_info["expires"])
            return 1
        return str(self.access["access"]["token"]["id"])

    @property
    def token_info(self):
        return self.access["access"]["token"]

    @property
    def token_is_valid(self):
        return (datetime.now() + timedelta(minutes=10)) < self.token_exp_date
    
