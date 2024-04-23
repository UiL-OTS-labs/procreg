import os

def discover(key):
    key = str(key)
    if key in os.listdir('/run/secrets/'):
        with open('/run/secrets/' + key) as file:
            return file.read().strip()
    elif key in os.environ:
        return os.environ.get(key)
    else:
        raise Exception("Failure: " + key + ' not found')

