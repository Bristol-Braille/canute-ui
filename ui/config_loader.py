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
    files_section['media_dir'] = os.path.expanduser(media_dir)

    return config

def import_pages(module):
    """
    return a dictionary of location -> module (such as buttons or view)
    from a list of subpackages
    """
    config = load()
    ui_section = config.get('ui', {})
    pages = ui_section.get('pages', [
        'library',
        'book',
        'go_to_page',
        'bookmarks_menu',
        'system_menu',
        'language',
        'encoding'
    ])
    return { p:__import__(f'{p}.{module}', globals(), fromlist=[None], level=1) for p in pages }
