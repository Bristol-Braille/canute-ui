import os.path

import toml

config_file = 'config.rc'

def load(config_file=config_file):
    if not os.path.exists(config_file):
        raise ValueError('Please provide a config.rc')

    config = toml.load(config_file)

    # expand any ~ home dirs in library paths
    library = config.get('files', {}).get('library', [])
    for entry in library:
        entry['path'] = os.path.expanduser(entry['path'])

    return config
