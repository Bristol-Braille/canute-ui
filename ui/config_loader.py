import os.path
from ConfigParser import ConfigParser

def load ():
    config = ConfigParser()
    config.read('config.rc')
    library_dir = config.get('files', 'library_dir')
    config.set('files', 'library_dir', os.path.expanduser(library_dir))
    return config
