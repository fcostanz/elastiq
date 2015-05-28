import pycurl
import json
import logging
import sys

import time

from utilities import slash

from instance import Instance
from flavor import Flavor
from image import Image
from keypair import KeyPair
from network import Network

from keystone import KeyStoneAPI
from nova import NovaAPI
from neutron import NeutronAPI

class OpenStackAPI:
    def __init__(self):
        logging.info("Initialization OpenStackAPI")
        self.keystone=KeyStoneAPI()
        self.nova=NovaAPI()
        self.neutron=NeutronAPI()
        
    def connect(self,**params):
        min_params=["keystone_url", "username", "password", "tenantName"]
        
        for p in min_params:
            try:
                params[p]
            except KeyError:
                logging.error("%s missing, not possible to establish connection", p)
                sys.exit(3)
    
        self.keystone.connect(username=params["username"], password=params["password"], url=params["keystone_url"])

        self.nova.tenant_id=self.keystone.tenant_id(params["tenantName"])
        try:
            self.nova.url=self.keystone.nova_url(params["tenantName"], params["nova_url"])
        except KeyError:
            self.nova.url=self.keystone.nova_url(params["tenantName"])
        if self.nova.url==None:
            logging.warning("Nova server not found")
            sys.exit(3)

        self.neutron.tenant_id=self.keystone.tenant_id(params["tenantName"])
        try:
            self.neutron.url=self.keystone.neutron_url(params["tenantName"], params["neutron_url"])
        except KeyError:
            self.neutron.url=self.keystone.neutron_url(params["tenantName"])
        if self.neutron.url==None:
            logging.warning("Neutron server not found")
            sys.exit(3)

        '''insts=self.nova.get_instances_list(token_id=self.keystone.token_id, tenant_id=self.keystone.tenant_id(params["tenantName"]))
        #for i in insts:
        #    print i.name, i.id

        flavors=self.nova.get_flavors_list(token_id=self.keystone.token_id, tenant_id=self.keystone.tenant_id(params["tenantName"]))
        #for f in flavors:
        #    print f.name, f.id

        keypairs=self.nova.get_keypairs_list(token_id=self.keystone.token_id, tenant_id=self.keystone.tenant_id(params["tenantName"]))
        #for k in keypairs:
        #    print k.name, k.public_key
        #print self.nova.get_keypair(token_id=self.keystone.token_id, tenant_id=self.keystone.tenant_id(params["tenantName"]), keypair_name="id_rsa_fcostanza").name

        images=self.nova.get_images_list(token_id=self.keystone.token_id, tenant_id=self.keystone.tenant_id(params["tenantName"]))
        #for i in images:
        #    print i.name, i.id

        networks=self.neutron.get_networks_list(token_id=self.keystone.token_id)
        #for n in networks:
        #    print n.name, n.id, n.status(token_id=self.keystone.token_id,server_url=self.neutron.url)

        net=self.neutron.get_network(token_id=self.keystone.token_id, network_name="oq-private-net")
        #print net.id

        #test running and terminate
        img=self.nova.get_image(token_id=self.keystone.token_id, tenant_id=self.keystone.tenant_id(params["tenantName"]), image_id="fd84dcc1-7322-41ef-b42e-2848a0fe1960")
        inst_id=img.run(token_id=self.keystone.token_id)

        inst=self.nova.get_instance(token_id=self.keystone.token_id, tenant_id=self.keystone.tenant_id(params["tenantName"]), instance_id=inst_id)

        status = ""
        count = 0
        while(count < 600):
            break
            status = inst.status(token_id=self.keystone.token_id)
            inst.update(token_id=self.keystone.token_id)
            print inst.addresses
            print status
            if status == "active":
                break
            time.sleep(10)
            count += 10            
        inst.terminate(token_id=self.keystone.token_id)'''

        
    def get_all_instances(self):
        return self.nova.get_instances_list(token_id=self.keystone.token_id)

    def get_all_flavors(self):
        return self.nova.get_flavors_list(token_id=self.keystone.token_id)

    def get_all_images(self):
        return self.nova.get_images_list(token_id=self.keystone.token_id)
        
    def get_all_keypairs(self):
        return self.nova.get_keypairs_list(token_id=self.keystone.token_id)

    def get_all_networks(self):
        return self.neutron.get_networks_list(token_id=self.keystone.token_id)

    def renew_token(self):
        return self.keystone.renew_token()

    @property
    def token_is_valid(self):
        return self.keystone.token_is_valid
