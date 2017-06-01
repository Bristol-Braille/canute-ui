import os.path
from ConfigParser import ConfigParser

config_file = 'config.rc'


def load(config_file=config_file):
    config = ConfigParser()
    c = config.read(config_file)
    if len(c) == 0:
        raise ValueError('Please provide a config.rc')
    library_dir = config.get('files', 'library_dir')
    config.set('files', 'library_dir', os.path.expanduser(library_dir))
    if not config.has_section('comms'):
        config.add_section('comms')
    if not config.has_option('comms', 'timeout'):
        config.set('comms', 'timeout', 60)
    return config
