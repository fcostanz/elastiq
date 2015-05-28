#!/usr/bin/python

# Test if OpenStackAPI  works by listing currently running instances. Uses env
# params: KEYSTONE_URL, KEYSTONE_USERNAME, KEYSTONE_PASSWORD + an optional
# optional param: TENANT_NAME

import pycurl
import json
import time

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

import sys
import os

from elastiq.plugins.OpenStackAPI import OpenStackAPI

def main():

    keystone_url = os.environ.get('KEYSTONE_URL')
    keystone_username = os.environ.get('KEYSTONE_USERNAME')
    keystone_password = os.environ.get('KEYSTONE_PASSWORD')
    tenant_name = os.environ.get('TENANT_NAME')

    print "Environment:"
    print "KEYSTONE_URL: %s" % keystone_url
    print "KEYSTONE_USERNAME: %s" % keystone_username
    print "KEYSTONE_PASSWORD: ############"
    print "TENANT_NAME: %s" % tenant_name

    if keystone_url is None or keystone_username is None or keystone_password is None:
        print "You must set all the proper KEYSTONE_* envvars for making it work."
        exit(1)

    try:
        api = OpenStackAPI()
        api.connect(keystone_url=keystone_url, username=keystone_username, password=keystone_password, tenantName=tenant_name)

        print "get reservations"
        res = api.get_all_instances()
        
        print "\n=== Instances ==="
        tenant_id=api.keystone.tenant_id(tenant_name)
        for i in res:
            print i.addresses
            #print "id=%s type=%s name=%s key=%s state=%s net=%s" % (i.id, api.nova.get_flavor(token_id=api.keystone.token_id, tenant_id=tenant_id, flavor_id=i.flavor_id).name, i.name, i.key_name, i.status(token_id=api.keystone.token_id))

        print "get images"  
        img = api.get_all_images()
    
        print "\n=== Images ==="
        for im in img:
            print "id=%s name=%s" % (im.id, im.name)
                    
    except Exception, e:
        print "OpenStackAPI can't talk to OpenStack servers: check your credentials."
        print "Error Message: %s", e
        exit(2)

# Execute main() function when invoked as an executable
if __name__ == "__main__":
    main()
