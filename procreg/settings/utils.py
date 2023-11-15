import os

def discover(key, default=None):
    key = str(key)
    if key in os.listdir('/run/secrets/'):
        with open('/run/secrets/' + key) as file:
            return file.read().strip()
    elif key in os.environ:
        return os.environ.get(key)
    else:
        if default is not None:
            return default
        raise Exception("Failure: " + key + ' not found')


def discover_list(key, default=None):
    try:
        raw = discover(key)
    except Exception as e:
        if default is not None:
            return default
        else:
            raise e
    return "\n".split(raw)
