from openStackObject import OpenStackObject

class KeyPair(OpenStackObject):
    def __init__(self, info=None):
        if info is None:
            self.name=None
            self.public_key=None
            self.fingerprint=None
        else:
            self.name=info["name"]
            self.public_key=info["public_key"]
            self.fingerprint=info["fingerprint"]
