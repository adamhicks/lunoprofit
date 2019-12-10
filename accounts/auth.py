from collections import namedtuple

APIAuth = namedtuple("APIAuth", "key secret")

def create_auth(key_file):
    with open(key_file) as f:
        lines = f.readlines()
    return APIAuth(lines[0].strip(), lines[1].strip())