import os.path
from configparser import ConfigParser

config_file = 'config.rc'


def load(config_file=config_file):
    config = ConfigParser()
    c = config.read(config_file)
    if len(c) == 0:
        raise ValueError('Please provide a config.rc')
    media_dir = config.get('files', 'media_dir')
    config.set('files', 'media_dir', os.path.expanduser(media_dir))
    if not config.has_section('comms'):
        config.add_section('comms')
    if not config.has_option('comms', 'timeout'):
        config.set('comms', 'timeout', 60)
    return config
