import os.path

import toml

config_file = 'config.rc'

def load(config_file=config_file):
    if not os.path.exists(config_file):
        raise ValueError('Please provide a config.rc')

    config = toml.load(config_file)

    # expand any ~ home dirs in media_dir
    files_section = config.get('files', {})
    media_dir = files_section.get('media_dir', '/media')
    files_section.set('media_dir', os.path.expanduser(media_dir))

    return config
